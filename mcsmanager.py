from playwright.async_api import async_playwright
import dotenv
import os
import asyncio
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="MCM.log", level=logging.INFO)

dotenv.load_dotenv()

async def start():
    logging.info("Starting up browser")
    async with async_playwright() as p:
        browser = await p.webkit.launch()
        page = await browser.new_page()
        logging.info("Visiting MCS portal")
        await page.goto("https://admin.tntcraft.xyz/#/login")

        logging.info("Logging In")
        await page.get_by_placeholder("Username").fill(os.getenv("UID"))

        await page.get_by_placeholder("Password").fill(os.getenv("PWD"))

        await page.get_by_text("Confirm").click()

        await page.wait_for_url("https://admin.tntcraft.xyz/#/")

        logging.info("Starting Vanilla in MCS portal")        
        await page.goto("https://admin.tntcraft.xyz/#/instances/terminal?daemonId=4bb133e0384b40c5aa2504c697dbfccc&instanceId=cde36cc7b6d0464792199b284cd4460b")

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
        await page.goto("https://admin.tntcraft.xyz/#/login")

        logging.info("Logging In")
        await page.get_by_placeholder("Username").fill(os.getenv("UID"))

        await page.get_by_placeholder("Password").fill(os.getenv("PWD"))

        await page.get_by_text("Confirm").click()

        await page.wait_for_url("https://admin.tntcraft.xyz/#/")

        logging.info("Starting Vanilla in MCS portal")        
        await page.goto("https://admin.tntcraft.xyz/#/instances/terminal?daemonId=4bb133e0384b40c5aa2504c697dbfccc&instanceId=cde36cc7b6d0464792199b284cd4460b")

        await page.get_by_role("button", name="Stop").click()

        await page.get_by_role("button",name="ok").click()

        await browser.close()
        logging.info("Browser has been Closed")