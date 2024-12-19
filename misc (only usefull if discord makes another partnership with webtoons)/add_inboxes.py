import asyncio
from main import MailMonitorClient

INBOXES = [
"3zt71qw06n9be7d7p4sxwju4s@freesourcecodes.com",
"tfbxs8e9alg5360ygtfxipmhnjx3aizpzms@freesourcecodes.com",
"hrrogqfr2d1deptzfdrqrkgbumlkbzj@freesourcecodes.com",
"gwfr7e54i746qhuj13xapf7fp9e6yk9o0luexmiykkqb@freesourcecodes.com",
"z9budeddkw9aaa9@freesourcecodes.com",
"ksbdanjm0k7pn2vrvky2la8sxmhf49rbrcdqfxgerogo@freesourcecodes.com",
"hsy8w3viglwzpslcc5mlmk0zvbn7ao@freesourcecodes.com",
]


async def main():
    client = MailMonitorClient()
    
    try:
        print("Connecting to server...")
        await client.connect()
        
        for inbox in INBOXES:
            print(f"Adding inbox: {inbox}")
            response = await client.add_inbox(inbox)
            print(f"Server response: {response['message']}")
            await asyncio.sleep(0.5)  # Small delay between requests
            
    except ConnectionRefusedError:
        print("Error: Could not connect to server. Make sure the server is running.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main()) 