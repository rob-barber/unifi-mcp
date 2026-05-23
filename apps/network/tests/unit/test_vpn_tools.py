"""Tests for VPN client/server state-update tool functions.

Locks in the preview-then-confirm behavior for the two mutating VPN tools.
"""

import os
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("UNIFI_HOST", "127.0.0.1")
os.environ.setdefault("UNIFI_USERNAME", "test")
os.environ.setdefault("UNIFI_PASSWORD", "test")


SAMPLE_CLIENT = {"_id": "vpnc1", "name": "Office WG", "enabled": True}
SAMPLE_SERVER = {"_id": "vpns1", "name": "Road Warriors", "enabled": False}


class TestUpdateVpnClientState:
    @pytest.mark.asyncio
    async def test_preview_returns_confirmation(self):
        with patch("unifi_network_mcp.tools.vpn.vpn_manager") as mock_mgr:
            mock_mgr.get_vpn_client_details = AsyncMock(return_value=SAMPLE_CLIENT)

            from unifi_network_mcp.tools.vpn import update_vpn_client_state

            result = await update_vpn_client_state(client_id="vpnc1", enabled=False, confirm=False)

        assert result["success"] is True
        assert result.get("requires_confirmation") is True
        assert result["preview"]["current"] == {"enabled": True}
        assert result["preview"]["proposed"] == {"enabled": False}

    @pytest.mark.asyncio
    async def test_default_confirm_is_preview(self):
        with patch("unifi_network_mcp.tools.vpn.vpn_manager") as mock_mgr:
            mock_mgr.get_vpn_client_details = AsyncMock(return_value=SAMPLE_CLIENT)
            mock_mgr.update_vpn_client_state = AsyncMock(return_value=True)

            from unifi_network_mcp.tools.vpn import update_vpn_client_state

            result = await update_vpn_client_state(client_id="vpnc1", enabled=False)

        assert result.get("requires_confirmation") is True
        mock_mgr.update_vpn_client_state.assert_not_called()

    @pytest.mark.asyncio
    async def test_confirm_true_executes(self):
        with patch("unifi_network_mcp.tools.vpn.vpn_manager") as mock_mgr:
            mock_mgr.update_vpn_client_state = AsyncMock(return_value=True)

            from unifi_network_mcp.tools.vpn import update_vpn_client_state

            result = await update_vpn_client_state(client_id="vpnc1", enabled=False, confirm=True)

        assert result["success"] is True
        assert "disabled" in result["message"]
        mock_mgr.update_vpn_client_state.assert_awaited_once_with("vpnc1", False)


class TestUpdateVpnServerState:
    @pytest.mark.asyncio
    async def test_preview_returns_confirmation(self):
        with patch("unifi_network_mcp.tools.vpn.vpn_manager") as mock_mgr:
            mock_mgr.get_vpn_server_details = AsyncMock(return_value=SAMPLE_SERVER)

            from unifi_network_mcp.tools.vpn import update_vpn_server_state

            result = await update_vpn_server_state(server_id="vpns1", enabled=True, confirm=False)

        assert result["success"] is True
        assert result.get("requires_confirmation") is True
        assert result["preview"]["current"] == {"enabled": False}
        assert result["preview"]["proposed"] == {"enabled": True}

    @pytest.mark.asyncio
    async def test_confirm_true_executes(self):
        with patch("unifi_network_mcp.tools.vpn.vpn_manager") as mock_mgr:
            mock_mgr.update_vpn_server_state = AsyncMock(return_value=True)

            from unifi_network_mcp.tools.vpn import update_vpn_server_state

            result = await update_vpn_server_state(server_id="vpns1", enabled=True, confirm=True)

        assert result["success"] is True
        assert "enabled" in result["message"]
        mock_mgr.update_vpn_server_state.assert_awaited_once_with("vpns1", True)
