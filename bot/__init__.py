"""Molty Royale AI Agent Bot"""
__version__ = "2.0.0"
__skill_version__ = "1.5.2"

from bot.airdrop import (
    AirdropConfig, AirdropManager, AirdropStatus, 
    AirdropClaim, AirdropRecord,
    get_airdrop_config, get_airdrop_manager,
)
from bot.api_client import MoltyAPI, APIError
from bot.credentials import (
    load_credentials, save_credentials,
    load_agent_wallet, save_agent_wallet,
    load_owner_wallet, save_owner_wallet,
    get_api_key, get_agent_private_key, get_owner_private_key,
)
from bot.state_router import determine_state, AIRDROP_PENDING
from bot.heartbeat import Heartbeat
