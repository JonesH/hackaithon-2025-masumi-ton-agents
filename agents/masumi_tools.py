"""
Masumi Network Tools for Agent Discovery and Hiring
Integrates with the Masumi MCP Server for decentralized agent operations
"""

import json
import os
from typing import Any, Dict, Optional

import httpx
from agno.tools import Toolkit


class MasumiTools(Toolkit):
    """Tools for interacting with the Masumi Network via MCP server"""

    def __init__(self):
        super().__init__(name="masumi_tools")

        # Register all Masumi-related tools
        self.register(self.list_agents)
        self.register(self.get_agent_input_schema)
        self.register(self.hire_agent)
        self.register(self.check_job_status)
        self.register(self.get_job_full_result)
        self.register(self.query_payments)
        self.register(self.get_purchase_history)
        self.register(self.query_registry)
        self.register(self.register_agent)
        self.register(self.unregister_agent)
        self.register(self.get_agents_by_wallet)

        # Load configuration from environment
        self.registry_base_url = os.getenv("MASUMI_REGISTRY_BASE_URL")
        self.payment_base_url = os.getenv("MASUMI_PAYMENT_BASE_URL")
        self.registry_token = os.getenv("MASUMI_REGISTRY_TOKEN")
        self.payment_token = os.getenv("MASUMI_PAYMENT_TOKEN")
        self.network = os.getenv("MASUMI_NETWORK", "Preprod")

    def _get_headers(self, service_type: str) -> Dict[str, str]:
        """Get appropriate headers for Masumi API calls"""
        if service_type == "registry":
            token = self.registry_token
        elif service_type == "payment":
            token = self.payment_token
        else:
            raise ValueError(f"Unknown service type: {service_type}")

        if not token:
            raise ValueError(f"Missing token for {service_type} service")

        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def list_agents(self, capability_filter: Optional[str] = None, price_max: Optional[float] = None) -> str:
        """
        List available agents from the Masumi Registry

        Args:
            capability_filter: Filter agents by capability (optional)
            price_max: Maximum price filter (optional)

        Returns:
            JSON string with agent list or error message
        """
        if not self.registry_base_url:
            return "Error: MASUMI_REGISTRY_BASE_URL not configured"

        try:
            url = f"{self.registry_base_url.rstrip('/')}/api/v1/registry-entry"
            headers = self._get_headers("registry")

            # Build query payload
            payload = {}
            if capability_filter:
                payload["capability"] = capability_filter
            if price_max:
                payload["priceMax"] = price_max

            with httpx.Client() as client:
                if payload:
                    response = client.post(url, headers=headers, json=payload)
                else:
                    response = client.get(url, headers=headers)

                response.raise_for_status()
                agents = response.json()

                if not agents:
                    return "No agents found matching the criteria"

                # Format the response nicely
                result = "Available Masumi Agents:\n\n"
                for agent in agents:
                    result += f"Agent ID: {agent.get('agentIdentifier', 'N/A')}\n"
                    result += f"Capability: {agent.get('capability', 'N/A')}\n"
                    result += f"Price: {agent.get('pricing', 'N/A')}\n"
                    result += f"Description: {agent.get('description', 'N/A')}\n"
                    result += "-" * 40 + "\n"

                return result

        except Exception as e:
            return f"Error listing agents: {str(e)}"

    def get_agent_input_schema(self, agent_identifier: str) -> str:
        """
        Get the input schema for a specific agent

        Args:
            agent_identifier: The unique identifier of the agent

        Returns:
            JSON string with input schema or error message
        """
        if not self.registry_base_url:
            return "Error: MASUMI_REGISTRY_BASE_URL not configured"

        try:
            url = f"{self.registry_base_url.rstrip('/')}/api/v1/payment-information"
            headers = self._get_headers("registry")
            params = {"agentIdentifier": agent_identifier}

            with httpx.Client() as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                schema_info = response.json()

                return f"Input Schema for Agent {agent_identifier}:\n{json.dumps(schema_info, indent=2)}"

        except Exception as e:
            return f"Error getting agent input schema: {str(e)}"

    def hire_agent(self, agent_identifier: str, input_data: Dict[str, Any], requested_funds: float) -> str:
        """
        Hire an agent and initiate payment

        Args:
            agent_identifier: The unique identifier of the agent
            input_data: Input data for the job
            requested_funds: Amount of funds to escrow for the job

        Returns:
            Job and payment information or error message
        """
        if not self.payment_base_url:
            return "Error: MASUMI_PAYMENT_BASE_URL not configured"

        try:
            url = f"{self.payment_base_url.rstrip('/')}/api/v1/payment"
            headers = self._get_headers("payment")

            payload = {
                "agentIdentifier": agent_identifier,
                "requestedFunds": requested_funds,
                "inputData": input_data,
                "network": self.network,
            }

            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

                payment_id = result.get("paymentId", "N/A")
                escrow_address = result.get("escrowAddress", "N/A")

                return f"""Agent Hired Successfully!

Agent: {agent_identifier}
Payment ID: {payment_id}
Escrow Address: {escrow_address}
Requested Funds: {requested_funds} ADA

Next Steps:
1. Send {requested_funds} ADA to the escrow address: {escrow_address}
2. Monitor job status using payment ID: {payment_id}
3. Results will be available once payment is confirmed and job completes

Full Response: {json.dumps(result, indent=2)}"""

        except Exception as e:
            return f"Error hiring agent: {str(e)}"

    def check_job_status(self, payment_id: str) -> str:
        """
        Check the status of a job/payment

        Args:
            payment_id: The payment ID from hire_agent

        Returns:
            Job status information or error message
        """
        if not self.payment_base_url:
            return "Error: MASUMI_PAYMENT_BASE_URL not configured"

        try:
            url = f"{self.payment_base_url.rstrip('/')}/api/v1/payment"
            headers = self._get_headers("payment")
            params = {"paymentId": payment_id}

            with httpx.Client() as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                status = response.json()

                payment_status = status.get("status", "Unknown")
                job_status = status.get("jobStatus", "Unknown")

                result = f"""Job Status for Payment {payment_id}:

Payment Status: {payment_status}
Job Status: {job_status}
Agent: {status.get('agentIdentifier', 'N/A')}
"""

                if "result" in status and status["result"]:
                    result += f"Result Preview: {str(status['result'])[:200]}...\n"

                if "escrowAddress" in status:
                    result += f"Escrow Address: {status['escrowAddress']}\n"

                result += f"\nFull Status: {json.dumps(status, indent=2)}"

                return result

        except Exception as e:
            return f"Error checking job status: {str(e)}"

    def get_job_full_result(self, payment_id: str) -> str:
        """
        Get the full result of a completed job

        Args:
            payment_id: The payment ID from hire_agent

        Returns:
            Full job result or error message
        """
        # First check status to see if job is complete
        status_result = self.check_job_status(payment_id)

        if "Error" in status_result:
            return status_result

        try:
            url = f"{self.payment_base_url.rstrip('/')}/api/v1/payment"
            headers = self._get_headers("payment")
            params = {"paymentId": payment_id, "fullResult": "true"}

            with httpx.Client() as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                result = response.json()

                if "result" not in result:
                    return "Job result not yet available. Please check job status first."

                return f"""Full Job Result for Payment {payment_id}:

Agent: {result.get('agentIdentifier', 'N/A')}
Status: {result.get('status', 'N/A')}

Result:
{json.dumps(result.get('result'), indent=2)}"""

        except Exception as e:
            return f"Error getting full job result: {str(e)}"

    def query_payments(self, agent_identifier: Optional[str] = None, status_filter: Optional[str] = None) -> str:
        """
        Query payment history

        Args:
            agent_identifier: Filter by specific agent (optional)
            status_filter: Filter by payment status (optional)

        Returns:
            Payment history or error message
        """
        if not self.payment_base_url:
            return "Error: MASUMI_PAYMENT_BASE_URL not configured"

        try:
            url = f"{self.payment_base_url.rstrip('/')}/api/v1/purchases"
            headers = self._get_headers("payment")
            params = {}

            if agent_identifier:
                params["agentIdentifier"] = agent_identifier
            if status_filter:
                params["status"] = status_filter

            with httpx.Client() as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                payments = response.json()

                if not payments:
                    return "No payments found matching the criteria"

                result = "Payment History:\n\n"
                for payment in payments:
                    result += f"Payment ID: {payment.get('paymentId', 'N/A')}\n"
                    result += f"Agent: {payment.get('agentIdentifier', 'N/A')}\n"
                    result += f"Status: {payment.get('status', 'N/A')}\n"
                    result += f"Amount: {payment.get('amount', 'N/A')}\n"
                    result += f"Date: {payment.get('createdAt', 'N/A')}\n"
                    result += "-" * 40 + "\n"

                return result

        except Exception as e:
            return f"Error querying payments: {str(e)}"

    def get_purchase_history(self) -> str:
        """
        Get complete purchase history for the current user

        Returns:
            Purchase history or error message
        """
        return self.query_payments()

    def query_registry(self, search_term: str) -> str:
        """
        Search the registry for agents matching a term

        Args:
            search_term: Term to search for in agent descriptions/capabilities

        Returns:
            Search results or error message
        """
        return self.list_agents(capability_filter=search_term)

    def register_agent(self, agent_data: Dict[str, Any]) -> str:
        """
        Register a new agent in the Masumi Registry

        Args:
            agent_data: Agent registration data

        Returns:
            Registration result or error message
        """
        if not self.payment_base_url:
            return "Error: MASUMI_PAYMENT_BASE_URL not configured"

        try:
            url = f"{self.payment_base_url.rstrip('/')}/api/v1/registry"
            headers = self._get_headers("payment")

            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=agent_data)
                response.raise_for_status()
                result = response.json()

                return f"Agent registered successfully: {json.dumps(result, indent=2)}"

        except Exception as e:
            return f"Error registering agent: {str(e)}"

    def unregister_agent(self, agent_identifier: str) -> str:
        """
        Unregister an agent from the Masumi Registry

        Args:
            agent_identifier: The unique identifier of the agent to unregister

        Returns:
            Unregistration result or error message
        """
        if not self.payment_base_url:
            return "Error: MASUMI_PAYMENT_BASE_URL not configured"

        try:
            url = f"{self.payment_base_url.rstrip('/')}/api/v1/registry/{agent_identifier}"
            headers = self._get_headers("payment")

            with httpx.Client() as client:
                response = client.delete(url, headers=headers)
                response.raise_for_status()

                return f"Agent {agent_identifier} unregistered successfully"

        except Exception as e:
            return f"Error unregistering agent: {str(e)}"

    def get_agents_by_wallet(self, wallet_address: str) -> str:
        """
        Get all agents registered by a specific wallet address

        Args:
            wallet_address: The wallet address to search for

        Returns:
            List of agents owned by the wallet or error message
        """
        if not self.registry_base_url:
            return "Error: MASUMI_REGISTRY_BASE_URL not configured"

        try:
            url = f"{self.registry_base_url.rstrip('/')}/api/v1/registry-entry"
            headers = self._get_headers("registry")
            payload = {"walletAddress": wallet_address}

            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                agents = response.json()

                if not agents:
                    return f"No agents found for wallet address: {wallet_address}"

                result = f"Agents owned by wallet {wallet_address}:\n\n"
                for agent in agents:
                    result += f"Agent ID: {agent.get('agentIdentifier', 'N/A')}\n"
                    result += f"Capability: {agent.get('capability', 'N/A')}\n"
                    result += f"Status: {agent.get('status', 'N/A')}\n"
                    result += "-" * 40 + "\n"

                return result

        except Exception as e:
            return f"Error getting agents by wallet: {str(e)}"
