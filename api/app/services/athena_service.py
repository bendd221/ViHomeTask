import asyncio
import aioboto3
from loguru import logger
from typing import List, Dict
from config import settings

class AsyncAthenaService:
    def __init__(self):
        self.session: aioboto3.Session = aioboto3.Session()
        self.region = settings.aws_region
        self.database = settings.athena_database
        self.output_location = settings.athena_output_location

    async def execute(self, query: str) -> List[Dict]:
        # Use an async context manager for the client
        async with self.session.client("athena", region_name=self.region) as client:
            logger.debug(f"Starting Athena Query Execution, query = {query}")
            response = await client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={"Catalog": "AWSDataCatalog", "Database": self.database},
                ResultConfiguration={"OutputLocation": self.output_location},
            )

            query_id = response["QueryExecutionId"]
            logger.debug(f"query_id = {query_id}")
            await self._wait(client, query_id)
            return await self._results(client, query_id)

    async def _wait(self, client, query_id: str) -> None:
        state = "RUNNING"
        max_executions = 20
        while max_executions > 0 and state in ["RUNNING", "QUEUED"]:
            max_executions -= 1
            status = await client.get_query_execution(QueryExecutionId=query_id)
            state = status["QueryExecution"]["Status"]["State"]

            if state == "SUCCEEDED":
                return
            if state in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"""
                    Athena query failed in state: {state}
                    Information: {status["QueryExecution"]["Status"]["AthenaError"]["ErrorMessage"]}
                """)

            await asyncio.sleep(0.5)

    async def _results(self, client, query_id: str) -> List[Dict]:
        paginator = client.get_paginator("get_query_results")

        headers = None
        results = []

        async for page in paginator.paginate(QueryExecutionId=query_id):
            rows = page["ResultSet"]["Rows"]

            if headers is None:
                headers = [col["VarCharValue"] for col in rows[0]["Data"]]
                rows = rows[1:]

            for row in rows:
                values = [col.get("VarCharValue") for col in row["Data"]]
                results.append(dict(zip(headers, values)))
        
        logger.debug(f"Query {query_id} finished, returning data.")
        return results
