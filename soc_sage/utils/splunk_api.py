import aiohttp
import asyncio
from dotenv import load_dotenv
from enum import Enum
import ssl
import time
import os
import xml.etree.ElementTree as ET


class JobsDispatchState(Enum):
    QUEUED = "QUEUED"
    PARSING = "PARSING"
    RUNNING = "RUNNING"
    FINALIZING = "FINALIZING"
    DONE = "DONE"
    PAUSE = "PAUSE"
    INTERNAL_CANCEL = "INTERNAL_CANCEL"
    USER_CANCEL = "USER_CANCEL"
    BAD_INPUT_CANCEL = "BAD_INPUT_CANCEL"
    QUIT = "QUIT"
    FAILED = "FAILED"


class SplunkApiCaller:
    """A caller class for Splunk REST API

    Attributes:
        base_url: The url of the splunk API.
        username: The username for API call.
        password: The password for the Splunk user.
        basic_auth: An instance of aiohttp BasicAuth.
        ssl_context: An SSL context for the self-signed certificate.
    """

    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv("SPLUNK_URL")
        self.username = os.getenv("SPLUNK_USER")
        self.password = os.getenv("SPLUNK_PASSWORD")

        self.basic_auth = aiohttp.BasicAuth(
            login=self.username, password=self.password
        )

        self.ssl_context = ssl.create_default_context()
        splunk_cert_state = os.getenv("SPLUNK_CERT")
        # If the splunk server uses the self-signed certificate,
        # disables SSL verification
        if splunk_cert_state == "self_signed":
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE

    async def create_search(self, spl_command: str) -> str | None:
        """Creates a search job on Splunk

        Calls the endpoint `search/jobs'.

        Args:
            spl_command: A string of spl commands

        Returns:
            A search ID of the job

        """
        endpoint = "services/search/jobs"

        payload = {"search": f"search {spl_command}"}
        async with aiohttp.ClientSession(self.base_url) as session:
            async with session.post(
                endpoint,
                auth=self.basic_auth,
                ssl=self.ssl_context,
                data=payload,
            ) as response:
                response_text = await response.text()
                root = ET.fromstring(response_text)
                search_id = root.findtext("sid")
                return search_id

    async def check_search_status(self, search_id: str) -> JobsDispatchState:
        """Retrieves the dispatch state of a Splunk search job.

        This function queries the Splunk REST API's `/services/search/jobs/{sid}`
        endpoint to get the current status of a specific search job.

        Args:
            search_id: The Search ID (SID) of the Splunk job.

        Returns:
            The string representing the dispatch state of the job (e.g., "DONE",
            "RUNNING", "QUEUED", "FAILED").
        """
        endpoint = f"services/search/jobs/{search_id}"

        async with aiohttp.ClientSession(self.base_url) as session:
            async with session.get(
                endpoint, auth=self.basic_auth, ssl=self.ssl_context
            ) as response:
                response_text = await response.text()
                root = ET.fromstring(response_text)
                xml_namespace = {"s": "http://dev.splunk.com/ns/rest"}
                dispatch_state_elememt = root.find(
                    ".//s:key[@name='dispatchState']", xml_namespace
                )
                return JobsDispatchState(dispatch_state_elememt.text)

    async def get_search_results(
        self,
        search_id: str,
        fields: list[str] | None = None,
        count: int | None = None,
    ):
        """Retrieves search results from a Splunk search job.

        Args:
            search_id: The unique identifier of the Splunk search job. This ID is
                       typically obtained when a search job is created.
            fields: A list of strings, where each string is the name of a field
                    to include in the search results. If an empty list is provided,
                    all available fields will be returned.
            count: An optional integer specifying the maximum number of results
                   to retrieve. If None, the Splunk API's default count limit
                   will apply (often 100).

        Returns:
            A dictionary of dictionaries representing the search results.
        """
        endpoint = f"services/search/v2/jobs/{search_id}/results"

        params = {"output_mode": "json"}
        if fields:
            params["f"] = fields

        if count:
            params["count"] = count

        async with aiohttp.ClientSession(self.base_url) as session:
            async with session.get(
                endpoint,
                auth=self.basic_auth,
                ssl=self.ssl_context,
                params=params,
            ) as response:
                response_json = await response.json()
                return response_json["results"]

    async def search(
        self,
        spl_command: str,
        output_fields: list[str] | None = None,
        output_count: int | None = None,
        polling_interval_seconds: int = 1,
        timeout_seconds: int = 60,
    ):
        """Creates a Splunk search job, polls its status, and retrieves the results.

        Args:
            spl_command: A string of spl search commands.
            output_fields: A list of strings, where each string is the name of a
                field to include in the search results. If an empty list is provided,
                all available fields will be returned.
            output_count: An optional integer specifying the maximum number of results
                to retrieve.
            polling_interval_seconds: How often to check the job status in seconds.
                Default is 1.
            timeout_seconds: Maximum time to wait for the search job to complete in
                seconds. Default is 60.

        Returns:
            A dictionary of dictionaries representing the search results.
        """
        search_id = await self.create_search(spl_command)

        start_time = time.time()
        while True:
            if time.time() - start_time > timeout_seconds:
                return None

            dispatch_state = await self.check_search_status(search_id)
            if dispatch_state == JobsDispatchState.DONE:
                break
            else:
                time.sleep(polling_interval_seconds)

        search_results = await self.get_search_results(
            search_id, fields=output_fields, count=output_count
        )
        return search_results
