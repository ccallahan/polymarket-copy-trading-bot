import traceback
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
from config import get_config

# Load configuration once at module level
config = get_config()

def validate_token_id(client: ClobClient, token_id: str) -> bool:
    """
    Validate that a token_id corresponds to an active market with an orderbook.
    
    Args:
        client: The ClobClient instance to use for validation
        token_id: The token ID to validate
        
    Returns:
        True if the token_id is valid and has an active orderbook, False otherwise
    """
    try:
        # Attempt to get the order book for this token
        # If the orderbook doesn't exist, this will raise an exception
        client.get_order_book(token_id)
        return True
    except Exception as e:
        # If we get an error, the token_id is likely invalid or the market is closed
        print(f"⚠️  Token validation failed for token_id={token_id}: {e}")
        return False

def make_order(price: float, size: float, side: str, token_id: str):
    try:
        print("\n" + "=" * 80)
        print("📝 CREATING NEW ORDER")
        print("=" * 80)
        print(f"💵 Price: {price}")
        print(f"📊 Size: {size}")
        print(f"↔️  Side: {side}")
        print(f"🎯 Token ID: {token_id}")
        print("=" * 80 + "\n")
        
        host: str = config.CLOB_API_URL
        key: str = config.PRIVATE_KEY  # This is your Private Key. Export from https://reveal.magic.link/polymarket or from your Web3 Extension
        chain_id: int = config.POLY_CHAIN_ID  # No need to adjust this
        POLYMARKET_PROXY_ADDRESS: str = config.POLY_FUNDER  # This is the address listed below your profile picture when using the Polymarket site.
        signature_type: int = config.POLY_SIGNATURE_TYPE  # Wallet signature type (0=EOA, 1=POLY_PROXY, 2=POLY_GNOSIS_SAFE)

        ### Initialization of a client using a Polymarket Proxy associated with an Email/Magic account. If you login with your email use this example.
        print("🔧 Initializing CLOB client...")
        client = ClobClient(host, key=key, chain_id=chain_id, signature_type=signature_type, funder=POLYMARKET_PROXY_ADDRESS)

        print("🔑 Setting API credentials...")
        client.set_api_creds(client.create_or_derive_api_creds())
        
        # Validate token_id before creating the order
        print("🔍 Validating token_id...")
        if not validate_token_id(client, token_id):
            print(f"❌ Validation failed: token_id {token_id} does not correspond to an active market")
            print(f"⚠️  Skipping order placement to avoid API error")
            print("=" * 80 + "\n")
            return None
        
        print("✅ Token validation successful")

        ## Create and sign a limit order buying 5 tokens for 0.010c each
        #Refer to the API documentation to locate a tokenID: https://docs.polymarket.com/developers/gamma-markets-api/fetch-markets-guide
        print("📋 Creating order arguments...")
        order_args = OrderArgs(
            price=price,
            size=size,
            side=side,
            token_id=token_id,
        )
        
        print("✍️  Signing order...")
        signed_order = client.create_order(order_args)
        
        ## GTC(Good-Till-Cancelled) Order
        print("📤 Posting order to exchange...")
        resp = client.post_order(signed_order, OrderType.GTC)
        
        print("\n" + "=" * 80)
        print("✅ ORDER PLACED SUCCESSFULLY")
        print("=" * 80)
        print(f"📄 Response: {resp}")
        print("=" * 80 + "\n")
        
        return resp
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR MAKING ORDER")
        print("=" * 80)
        print(f"💵 Price: {price}")
        print(f"📊 Size: {size}")
        print(f"↔️  Side: {side}")
        print(f"🎯 Token ID: {token_id}")
        print(f"🚨 Error: {e}")
        print("=" * 80)
        print("📋 Full traceback:")
        traceback.print_exc()
        print("=" * 80 + "\n")
        return None

if __name__ == "__main__":
    make_order(price=0.071, size=14.1, side=BUY, token_id='27745789011483877770092220164639878505910623464021791529418856008078952259643')

    