"""
State router — determines agent state from GET /accounts/me response.
Routes per skill.md State Router logic.
"""
from bot.utils.logger import get_logger
from bot.config import ENABLE_AIRDROP

log = get_logger(__name__)

# States
NO_ACCOUNT = "NO_ACCOUNT"
NO_IDENTITY = "NO_IDENTITY"
IN_GAME = "IN_GAME"
READY_PAID = "READY_PAID"
READY_FREE = "READY_FREE"
AIRDROP_PENDING = "AIRDROP_PENDING"
ERROR = "ERROR"


def determine_state(me_response: dict, airdrop_available: bool = False) -> tuple[str, dict]:
    """
    Analyze /accounts/me response → return (state, context).
    Context contains relevant data for the next step.
    
    Args:
        me_response: Response from GET /accounts/me
        airdrop_available: Whether there are pending airdrops to claim
    """
    readiness = me_response.get("readiness", {})
    current_games = me_response.get("currentGames", [])

    # Check for airdrop first (if enabled and available)
    if ENABLE_AIRDROP and airdrop_available:
        log.info("Airdrop available for claiming")
        return AIRDROP_PENDING, {
            "balance": me_response.get("balance", 0),
            "wallet_address": readiness.get("walletAddress"),
        }

    # Check for active game
    for game in current_games:
        if game.get("gameStatus") in ("waiting", "running"):
            log.info("Active game found: %s (status=%s)",
                     game["gameId"], game["gameStatus"])
            return IN_GAME, {
                "game_id": game["gameId"],
                "agent_id": game["agentId"],
                "game_status": game["gameStatus"],
                "entry_type": game.get("entryType", "free"),
                "is_alive": game.get("isAlive", True),
            }

    # Check ERC-8004 identity
    erc8004_id = readiness.get("erc8004Id")
    if erc8004_id is None:
        log.info("No ERC-8004 identity registered")
        return NO_IDENTITY, {}

    # Check paid readiness
    if readiness.get("paidReady", False):
        balance = me_response.get("balance", 0)
        if balance >= 500:  # PAID_ENTRY_FEE_SMOLTZ from economy.md
            log.info("Paid ready: balance=%d sMoltz", balance)
            return READY_PAID, {"balance": balance}

    # Default to free
    log.info("Ready for free play")
    return READY_FREE, {
        "balance": me_response.get("balance", 0),
        "wallet_address": readiness.get("walletAddress"),
        "whitelist_approved": readiness.get("whitelistApproved", False),
    }
