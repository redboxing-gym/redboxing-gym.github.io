"""Actual homepage layout, interaction, lifecycle and virtual/real timer checks."""
import os
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import test_category_filters_browser as fixture


@unittest.skipUnless(os.environ.get('RUN_BROWSER_TESTS') == '1',
                     'Set RUN_BROWSER_TESTS=1 for homepage Chromium checks')
class HomeArticleBrowserTests(unittest.TestCase):
    setUpClass = classmethod(fixture.CategoryFilterBrowserTests.setUpClass.__func__)
    screenshot = fixture.CategoryFilterBrowserTests.screenshot

    def home(self, width=1440, javascript=True, clock=True):
        context = self.browser.new_context(viewport={'width': width, 'height': 1000},
                                           has_touch=width < 992, java_script_enabled=javascript)
        self.addCleanup(context.close)
        context.route('https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css',
                      lambda route: route.fulfill(body=self.bootstrap, content_type='text/css'))
        page = context.new_page()
        if javascript and clock:
            now = datetime(2026, 11, 6, tzinfo=timezone.utc)
            page.clock.install(time=now)
            page.clock.pause_at(now + timedelta(seconds=1))
        page.goto(self.url + '/', wait_until='networkidle')
        if javascript:
            page.locator('[data-home-ready="true"]').wait_for()
        page.mouse.move(0, 0)
        return page

    def selected(self, page):
        return page.locator('#articles [role="tab"][aria-selected="true"]').get_attribute('id')

    def release(self, page):
        page.evaluate('document.activeElement.blur()')
        # The full-width section can cover viewport (0, 0) after scrolling.
        # Hover the existing fixed menu, which is outside the article region.
        page.locator('.menu-toggle').hover()

    def position(self, page):
        return page.evaluate('''() => ({
            scroll: scrollY, width: document.documentElement.scrollWidth,
            stage: document.querySelector('[data-home-stage]').getBoundingClientRect().height,
            contact: document.querySelector('#contact').getBoundingClientRect().top + scrollY
        })''')

    def test_layout_limits_geometry_cta_and_map_stability(self):
        for width in [360, 390, 1440]:
            with self.subTest(width=width):
                page = self.home(width, clock=False)
                page.locator('#home-articles-title').scroll_into_view_if_needed()
                before = self.position(page)
                self.assertLessEqual(before['width'], width)
                tabs = page.locator('#articles [role="tab"]')
                self.assertEqual(tabs.count(), 5)
                self.assertEqual(tabs.all_text_contents(),
                                 ['경기 분석', '복싱 기술', '운동과학', '복싱 입문', '운동 프로그램'])
                for i in range(tabs.count()):
                    tabs.nth(i).click()
                    cards = page.locator('#articles [data-article-card]:visible')
                    self.assertEqual(cards.count(), 2 if width < 992 else 4)
                    boxes = cards.evaluate_all('(cards) => cards.map(c => {const r = c.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width};})')
                    if width < 992:
                        self.assertAlmostEqual(boxes[0]['x'], boxes[1]['x'], delta=1)
                        self.assertGreater(boxes[1]['y'], boxes[0]['y'])
                    else:
                        self.assertAlmostEqual(boxes[0]['y'], boxes[1]['y'], delta=1)
                        self.assertAlmostEqual(boxes[2]['y'], boxes[3]['y'], delta=1)
                        self.assertGreater(boxes[1]['x'], boxes[0]['x'])
                        self.assertGreater(boxes[2]['y'], boxes[0]['y'])
                    image_rules = page.locator('#articles .article-card:visible img').first.evaluate(
                        '(i) => ({fit:getComputedStyle(i).objectFit,min:getComputedStyle(i).minHeight})')
                    self.assertEqual(image_rules, {'fit': 'cover', 'min': '288px'})
                    now = self.position(page)
                    self.assertAlmostEqual(now['stage'], before['stage'], delta=1)
                    self.assertAlmostEqual(now['contact'], before['contact'], delta=1)
                self.assertEqual(page.get_by_role('link', name='전체 아티클 보기').get_attribute('href'),
                                 '/articles/index.html')
                self.assertEqual(page.locator('#contact iframe').count(), 2)
                tabs.first.click()
                self.screenshot(page, f'home-rotation-{width}')
                if os.environ.get('QA_OUTPUT_DIR'):
                    page.locator('#articles').screenshot(path=str(
                        Path(os.environ['QA_OUTPUT_DIR']) / f'home-section-{width}.png'))
                print('HOME_LAYOUT', width, boxes, self.position(page))

    def test_ten_seconds_wraparound_and_manual_timer_reset(self):
        page = self.home()
        tabs = page.locator('#articles [role="tab"]')
        ids = [tabs.nth(i).get_attribute('id') for i in range(tabs.count())]
        page.clock.run_for(9999)
        self.assertEqual(self.selected(page), ids[0])
        page.clock.run_for(1)
        self.assertEqual(self.selected(page), ids[1])
        for expected in ids[2:] + ids[:1]:
            page.clock.run_for(10000)
            self.assertEqual(self.selected(page), expected)
        page.clock.run_for(9000)
        tabs.nth(2).click()
        self.release(page)
        page.clock.run_for(9999)
        self.assertEqual(self.selected(page), ids[2])
        page.clock.run_for(1)
        self.assertEqual(self.selected(page), ids[3])

    def test_keyboard_focus_hover_and_lifecycle_pause(self):
        page = self.home()
        tabs = page.locator('#articles [role="tab"]')
        tabs.first.focus()
        page.keyboard.press('ArrowRight')
        self.assertEqual(tabs.nth(1).get_attribute('aria-selected'), 'true')
        page.clock.run_for(20000)
        self.assertEqual(page.locator(':focus').get_attribute('id'), tabs.nth(1).get_attribute('id'))
        self.assertEqual(tabs.nth(1).get_attribute('aria-selected'), 'true')
        page.keyboard.press('End')
        self.assertEqual(tabs.last.get_attribute('aria-selected'), 'true')
        page.keyboard.press('Home')
        self.assertEqual(tabs.first.get_attribute('aria-selected'), 'true')
        page.get_by_role('button', name='다음 카테고리').focus()
        page.keyboard.press('Enter')
        self.assertEqual(tabs.nth(1).get_attribute('aria-selected'), 'true')
        page.get_by_role('button', name='이전 카테고리').focus()
        page.keyboard.press('Space')
        self.assertEqual(tabs.first.get_attribute('aria-selected'), 'true')
        self.release(page)
        page.locator('#articles .article-card:visible').first.hover()
        page.clock.run_for(20000)
        self.assertEqual(tabs.first.get_attribute('aria-selected'), 'true')
        self.release(page)
        # Drive lifecycle events explicitly: headless tabs do not always expose
        # OS visibility changes. Real-time rotation is checked separately below.
        page.evaluate("Object.defineProperty(document, 'hidden', {configurable:true,value:true}); document.dispatchEvent(new Event('visibilitychange'))")
        page.clock.run_for(20000)
        self.assertEqual(tabs.first.get_attribute('aria-selected'), 'true')
        page.evaluate("delete document.hidden; document.dispatchEvent(new Event('visibilitychange')); window.dispatchEvent(new Event('blur'))")
        page.clock.run_for(20000)
        self.assertEqual(tabs.first.get_attribute('aria-selected'), 'true')
        page.evaluate("window.dispatchEvent(new Event('focus'))")
        page.evaluate("""() => {
            window.motionUpdates = 0;
            matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',
                () => { window.motionUpdates += 1; });
        }""")
        page.emulate_media(reduced_motion='reduce')
        page.wait_for_function('window.motionUpdates === 1', polling=50)
        page.clock.run_for(20000)
        self.assertEqual(tabs.first.get_attribute('aria-selected'), 'true')
        page.emulate_media(reduced_motion='no-preference')
        # Wait for Chromium to actually dispatch the native change event, after
        # the app's earlier listener has reset its timer. A fixed frame delay
        # races with media emulation while the JavaScript clock is paused.
        page.wait_for_function('window.motionUpdates === 2', polling=50)
        page.clock.run_for(10000)
        self.assertEqual(tabs.nth(1).get_attribute('aria-selected'), 'true')

    def test_touch_swipe_vertical_scroll_drag_pause_and_link_click(self):
        page = self.home(390)
        first = self.selected(page)
        stage = page.locator('[data-home-stage]')
        page.locator('#articles .article-card:visible img').first.scroll_into_view_if_needed()
        session = page.context.new_cdp_session(page)
        def touch(kind, x=0, y=0):
            session.send('Input.dispatchTouchEvent', {
                'type': kind, 'touchPoints': [] if kind == 'touchEnd' else [{'x': x, 'y': y}]})
        touch('touchStart', 300, 350)
        page.clock.run_for(20000)
        self.assertEqual(self.selected(page), first)
        touch('touchMove', 220, 352)
        touch('touchMove', 100, 354)
        touch('touchEnd')
        self.assertNotEqual(self.selected(page), first)
        self.assertEqual(page.url, self.url + '/')
        second = self.selected(page)
        self.release(page)
        page.clock.run_for(9999)
        self.assertEqual(self.selected(page), second)
        # Reset with an ordinary vertical gesture: browser scrolling must work.
        old_scroll = page.evaluate('scrollY')
        touch('touchStart', 200, 450)
        touch('touchMove', 202, 350)
        touch('touchMove', 204, 250)
        touch('touchEnd')
        self.assertEqual(self.selected(page), second)
        self.assertGreater(page.evaluate('scrollY'), old_scroll)
        # A fresh normal tap after the swipe must navigate to the real article.
        link = page.locator('#articles .article-card:visible').first
        expected = link.get_attribute('href')
        link.tap()
        page.wait_for_url(self.url + expected)

    def test_no_javascript_bounded_default_and_cta(self):
        for width in [390, 1440]:
            page = self.home(width, javascript=False)
            self.assertFalse(page.locator('[data-home-controls]').is_visible())
            self.assertEqual(page.locator('#articles [data-home-panel]:visible').count(), 1)
            self.assertEqual(page.locator('#articles .article-card:visible').count(), 2 if width < 992 else 4)
            self.assertEqual(page.get_by_role('link', name='전체 아티클 보기').get_attribute('href'),
                             '/articles/index.html')
            page.locator('#home-articles-title').scroll_into_view_if_needed()
            self.screenshot(page, f'home-no-javascript-{width}')

    def test_existing_breakpoint_and_height_recalculation_after_resize(self):
        page = self.home(390, clock=False)
        mobile_height = self.position(page)['stage']
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.wait_for_function('''height => document.querySelector('[data-home-stage]')
            .getBoundingClientRect().height < height''', arg=mobile_height)
        self.assertEqual(page.locator('#articles .article-card:visible').count(), 4)
        for width, count in [(991, 2), (992, 4), (360, 2)]:
            page.set_viewport_size({'width': width, 'height': 1000})
            page.wait_for_function('''count => [...document.querySelectorAll('#articles [data-article-card]')]
                .filter(c => c.getBoundingClientRect().width > 0).length === count''', arg=count)
            self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)

    def test_guide_menu_order_scroll_close_and_cross_page_navigation(self):
        for width in [360, 390, 1440]:
            with self.subTest(width=width):
                page = self.home(width, clock=False)
                sidebar = page.locator('#sidebar-wrapper')
                page.locator('.menu-toggle').click()
                links = sidebar.locator('.sidebar-nav-item a')
                self.assertEqual(links.all_text_contents()[3:6], ['시설', '복싱 가이드', '이용안내'])
                guide = sidebar.get_by_role('link', name='복싱 가이드', exact=True)
                self.assertEqual(guide.get_attribute('href'), '/#articles')
                self.assertEqual(guide.get_attribute('class'), 'js-scroll-trigger')
                page.wait_for_function("Math.abs(document.querySelector('#sidebar-wrapper').getBoundingClientRect().left - (innerWidth - 250)) < 1")
                self.screenshot(page, f'guide-menu-{width}')
                documents = []
                page.on('request', lambda request: documents.append(request.url)
                        if request.is_navigation_request() and request.frame == page.main_frame else None)
                guide.click()
                page.wait_for_url(self.url + '/#articles')
                page.wait_for_function("Math.abs(document.querySelector('#articles').getBoundingClientRect().top) < 2")
                self.assertNotIn('active', sidebar.get_attribute('class') or '')
                self.assertNotIn('active', page.locator('.menu-toggle').get_attribute('class'))
                page.wait_for_function("document.querySelector('#sidebar-wrapper').getBoundingClientRect().left >= innerWidth")
                self.assertEqual(documents, [])  # Native same-document smooth anchor.
                title = page.locator('#home-articles-title').bounding_box()
                self.assertGreaterEqual(title['y'], 65)
                self.assertLess(title['y'] + title['height'], 1000)
                self.assertEqual(page.get_by_role('link', name='전체 아티클 보기').get_attribute('href'),
                                 '/articles/index.html')
                # Neighbouring existing menus keep their anchor and close behaviour.
                for label, target in [('시설', '#facility'), ('이용안내', '#price')]:
                    page.locator('.menu-toggle').click()
                    link = sidebar.get_by_role('link', name=label, exact=True)
                    self.assertEqual(link.get_attribute('href'), target)
                    link.click()
                    page.wait_for_function("id => Math.abs(document.querySelector(id).getBoundingClientRect().top) < 2",
                                           arg=target)
                    self.assertNotIn('active', sidebar.get_attribute('class') or '')
                for path in ['/articles/index.html', '/articles/boxing-breathing-basics.html']:
                    page.goto(self.url + path, wait_until='networkidle')
                    page.locator('.article-nav').get_by_role('link', name='복싱 가이드', exact=True).click()
                    page.wait_for_url(self.url + '/#articles')
                    page.wait_for_load_state('networkidle')
                    # Native cross-document anchors can settle a few pixels
                    # differently after fonts/images load; require the complete
                    # heading to be visible below the existing fixed menu.
                    page.wait_for_function("""() => {
                        const r = document.querySelector('#home-articles-title').getBoundingClientRect();
                        return r.top >= 65 && r.bottom < innerHeight;
                    }""")
                    self.assertGreaterEqual(page.locator('#home-articles-title').bounding_box()['y'], 65)
                    self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)

    def test_real_time_rotation_scroll_position_and_no_extra_requests(self):
        page = self.home(clock=False)
        page.locator('#home-articles-title').scroll_into_view_if_needed()
        self.release(page)
        initial = self.selected(page)
        before = self.position(page)
        requests = []
        page.on('request', lambda request: requests.append(request.url))
        start = time.monotonic()
        page.wait_for_function("id => document.querySelector('#articles [aria-selected=\"true\"]').id !== id",
                               arg=initial, timeout=12500)
        elapsed = time.monotonic() - start
        self.assertGreater(elapsed, 8)
        self.assertLess(elapsed, 12)
        self.assertEqual(self.position(page), before)
        self.assertEqual(requests, [])
        self.assertEqual(page.locator('[data-home-stage]').get_attribute('aria-live'), 'off')
        print('HOME_REAL_TIMER_SECONDS', elapsed)


if __name__ == '__main__':
    unittest.main()
