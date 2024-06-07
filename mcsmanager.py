from playwright.async_api import async_playwright
import dotenv
import os
import asyncio
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="MCM.log", level=logging.INFO)

dotenv.load_dotenv()

daemonID = os.getenv('daemonID')
instanceID = os.getenv('instanceID')

async def start():
    logging.info("Starting up browser")
    async with async_playwright() as p:
        browser = await p.webkit.launch(headless=False)
        page = await browser.new_page()
        logging.info("Visiting MCS portal")
        await page.goto("localhost:23333/#/login")

        

        logging.info("Logging In")
        await page.get_by_placeholder("Username").fill(os.getenv("UID"))

        await page.get_by_placeholder("Password").fill(os.getenv("PWD"))

        await page.get_by_text("Confirm").click()

        await page.wait_for_url("http://localhost:23333/#/")

        logging.info("Starting Vanilla in MCS portal")        
        await page.goto(f"localhost:23333/#/instances/terminal?daemonId={daemonID}&instanceId={instanceID}")

        await page.get_by_role("button", name="Start").click()

        await page.get_by_role("button",name="ok").click()

        await browser.close()
        logging.info("Browser has been Closed")

async def stop():
    logging.info("Starting up browser")
    async with async_playwright() as p:
        browser = await p.webkit.launch()
        page = await browser.new_page()
        logging.info("Visiting MCS portal")
        await page.goto("localhost:23333/#/login")

        logging.info("Logging In")
        await page.get_by_placeholder("Username").fill(os.getenv("UID"))

        await page.get_by_placeholder("Password").fill(os.getenv("PWD"))

        await page.get_by_text("Confirm").click()

        await page.wait_for_url("localhost:23333/#/")

        logging.info("Stopping Vanilla in MCS portal")        
        await page.goto(f"localhost:23333/#/instances/terminal?daemonId={daemonID}&instanceId={instanceID}")

        await page.get_by_role("button", name="Stop").click()

        await page.get_by_role("button",name="ok").click()

        await browser.close()
        logging.info("Browser has been Closed")