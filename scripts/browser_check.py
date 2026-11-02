"""Optional local browser QA. Requires Playwright and Chromium."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
R=Path(__file__).resolve().parents[1]
errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1440,'height':1080},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8000/',wait_until='networkidle')
 page.wait_for_selector('#viewer[data-loaded="true"]',timeout=60000)
 page.evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager')")
 page.wait_for_function("Array.from(document.images).every(i=>i.complete)")
 page.wait_for_timeout(1200)
 page.screenshot(path='/tmp/beret-desktop.png',full_page=True)
 print('initial',page.evaluate('window.beretState()'))
 page.locator('[data-mode="open"]').click();page.wait_for_function('window.beretState().angle > 100',timeout=20000)
 state=page.evaluate('window.beretState()');assert state['angle']>100,state
 page.screenshot(path='/tmp/beret-open.png')
 page.locator('[data-mode="explode"]').click();page.wait_for_function('window.beretState().lift > 36',timeout=20000)
 state=page.evaluate('window.beretState()');assert state['lift']>36,state
 page.locator('[data-mode="cavity"]').click();page.wait_for_function('window.beretState().flip > 3.1',timeout=20000)
 state=page.evaluate('window.beretState()');assert state['flip']>3.1,state
 page.locator('[data-color="sage"]').click();assert page.locator('#color-name').inner_text()=='苔绿帽'
 page.locator('#lid-angle').evaluate('(e)=>{e.value=60;e.dispatchEvent(new Event("input",{bubbles:true}))}')
 page.wait_for_function('Math.abs(window.beretState().angle - 60)<1',timeout=20000);state=page.evaluate('window.beretState()');assert abs(state['angle']-60)<1,state
 page.locator('[data-view="back"]').click();page.wait_for_timeout(800)
 page.locator('#reset-view').click();page.wait_for_function('window.beretState().angle < .5',timeout=20000)
 page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(800)
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'mobile overflow'
 page.screenshot(path='/tmp/beret-mobile.png',full_page=True)
 assert not errors,errors
 print('interaction checks passed; browser errors:',errors)
 # Ensure fallback works for browsers without WebGL.
 fallback=b.new_page(viewport={'width':390,'height':844})
 fallback.add_init_script("HTMLCanvasElement.prototype.getContext = () => null")
 fallback.goto('http://127.0.0.1:8000/',wait_until='networkidle');fallback.wait_for_selector('#fallback:not([hidden])')
 assert not fallback.locator('#poster').is_hidden()
 print('WebGL fallback passed')
 b.close()
