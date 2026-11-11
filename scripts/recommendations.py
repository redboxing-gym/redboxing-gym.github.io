"""Deterministic, offline recommendations from public article metadata.

No body text, manual ``related`` values, URLs or dates contribute topic points.
Dates and URLs only break ties. See docs/article-recommendations.md for the
scoring table, token limitations and the four disjoint selection stages.
"""
from dataclasses import dataclass
from datetime import date
import json
import re
import unicodedata


RELATED_CATEGORIES = {
    'boxing-technique': ('boxing-beginners', 'workout-programs'),
    'boxing-beginners': ('boxing-technique', 'workout-programs'),
    'exercise-science': ('workout-programs', 'weight-management', 'boxing-technique'),
    'workout-programs': ('exercise-science', 'weight-management', 'boxing-beginners'),
    'weight-management': ('exercise-science', 'workout-programs'),
    'match-analysis': ('boxing-technique', 'combat-history'),
    'combat-culture': ('combat-history', 'match-analysis'),
    'combat-history': ('match-analysis', 'combat-culture'),
}

# Site/reader/format words cannot establish a specific topic by themselves.
# This is a small stop list, not a required vocabulary for authors or tag IDs.
GENERAL_WORDS = frozenset('''
    복싱 운동 운동과학 격투기 경기 분석 기술 입문 초보 초보자 기초 기본
    레드복싱 행신 행신동 행신점 을지로 을지로점 체육관 복싱장
    가이드 안내 방법 요령 배우기 알아보기 정리 소개 설명 참고 자료
    연습 훈련 수업 코칭 프로그램 추천 리뷰 관전 이야기 처음 시작
    하는 하기 치는 치기 위한 위해 함께 통해 대한 대해 어떤 어떻게
    무엇 왜 때 법 수 것 점 더 잘 전 후 중 및 등 있는 없는 있습니다
    boxing exercise workout beginner beginners training guide red redboxing
'''.split())
SHORT_TOPICS = frozenset({'잽', '훅', '땀'})
KOREAN_SUFFIXES = ('으로는', '에서는', '에게는', '으로', '에서', '에게',
                   '에는', '은', '는', '이', '가', '을', '를', '의', '와', '과', '도', '로', '에')
DIRECT_SCORE = 4
DESCRIPTIVE_FIELDS = ('description', 'lead', 'kicker')


def topic_tokens(text):
    """NFKC/casefold words, conservative Korean particle removal, no substrings.

    Keep two-character words and the explicit one-character topic exceptions.
    Numeric-only and general words are discarded. No morphology or synonyms.
    """
    words = re.findall(r'[^\W_]+', unicodedata.normalize('NFKC', text).casefold())
    result = []
    for word in words:
        # Check before stripping so general words such as '하는' stay general.
        if word in GENERAL_WORDS:
            continue
        for suffix in KOREAN_SUFFIXES:
            stem = word[:-len(suffix)]
            if word.endswith(suffix) and (len(stem) >= 2 or stem in SHORT_TOPICS):
                word = stem
                break
        if (word not in GENERAL_WORDS and not word.isnumeric()
                and (len(word) >= 2 or word in SHORT_TOPICS)):
            result.append(word)
    return tuple(result)


@dataclass(frozen=True)
class Topics:
    tags: frozenset
    keywords: frozenset
    title: tuple
    descriptions: tuple

    @property
    def phrases(self):
        return self.tags | self.keywords


def article_topics(article):
    def phrases(field):
        return frozenset(tokens for value in article.get(field, [])
                         if (tokens := topic_tokens(value)))
    return Topics(phrases('tags'), phrases('keywords'),
                  topic_tokens(article.get('title', '')),
                  tuple(topic_tokens(article.get(field, '')) for field in DESCRIPTIVE_FIELDS))


def contains_phrase(words, phrase):
    return any(words[i:i + len(phrase)] == phrase
               for i in range(len(words) - len(phrase) + 1))


def score_topics(left, right):
    """Symmetric score; each evidence family counts at most 3 distinct matches.

    Exact specific tags/keywords: 24/20; tag-keyword cross-match: 16.
    Topic phrases in the other title/descriptive metadata: 8/4.
    Shared title words: 2; title-to-descriptive-metadata words: 1.
    A score >= 4 qualifies as direct relevance, independent of category.
    """
    title_phrases = {p for p in left.phrases if contains_phrase(right.title, p)}
    title_phrases |= {p for p in right.phrases if contains_phrase(left.title, p)}
    description_phrases = {p for p in left.phrases
                           if any(contains_phrase(words, p) for words in right.descriptions)}
    description_phrases |= {p for p in right.phrases
                            if any(contains_phrase(words, p) for words in left.descriptions)}
    left_description = {word for words in left.descriptions for word in words}
    right_description = {word for words in right.descriptions for word in words}
    evidence = (
        (24, left.tags & right.tags),
        (20, left.keywords & right.keywords),
        (16, (left.tags & right.keywords) | (left.keywords & right.tags)),
        (8, title_phrases),
        (4, description_phrases),
        (2, set(left.title) & set(right.title)),
        (1, (set(left.title) & right_description) | (set(right.title) & left_description)),
    )
    return sum(weight * min(3, len(matches)) for weight, matches in evidence)


def relevance_score(left, right):
    """Public scoring helper for review/tests, without mutating either article."""
    return score_topics(article_topics(left), article_topics(right))


def recommend_related(article, catalog):
    """Return up to 3 unique public articles in stage/score/date/URL order.

    Missing draft flags identify legacy public records. A catalog with >= 3
    eligible unique URLs always returns 3. Associated categories form one pool;
    their table order does not override score/date/URL ordering within stage 3.
    """
    if article.get('draft', False):
        return []
    source = article_topics(article)
    category = article['category']
    ranked = []
    for candidate in catalog:
        if candidate.get('draft', False) or candidate['url'] == article['url']:
            continue
        score = score_topics(source, article_topics(candidate))
        if score >= DIRECT_SCORE:
            stage = 0
        elif candidate['category'] == category:
            stage = 1
        elif candidate['category'] in RELATED_CATEGORIES.get(category, ()):
            stage = 2
        else:
            stage = 3
        # Extra signature only resolves conflicting duplicate URL records; it
        # excludes related/body and never changes ordering of distinct URLs.
        signature = json.dumps({key: candidate.get(key) for key in (
            'category', 'title', *DESCRIPTIVE_FIELDS, 'tags', 'keywords')},
            sort_keys=True, ensure_ascii=False)
        ranked.append(((stage, -score, -date.fromisoformat(str(candidate['published'])).toordinal(),
                        candidate['url'], signature), candidate))
    result, seen = [], set()
    for _, candidate in sorted(ranked, key=lambda item: item[0]):
        if candidate['url'] not in seen:
            result.append(candidate)
            seen.add(candidate['url'])
        if len(result) == 3:
            break
    return result
