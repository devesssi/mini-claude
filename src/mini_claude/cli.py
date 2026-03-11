import click
import sys
from colorama import Fore, Style, init
from .config import save_api_key, load_api_key
from .core.engine import OpenCodeEngine

# Initialize colorama for Windows/Linux/Mac support
init(autoreset=True)

@click.group()
def main():
    """Mini-Claude: An autonomous AI coding agent."""
    pass

@main.command()
def configure():
    """Step 1: Save your Groq API Key."""
    click.echo(f"{Fore.CYAN}--- Mini-Claude Configuration ---")
    key = click.prompt(f"{Fore.YELLOW}Enter your Groq API Key", hide_input=True)
    if key.startswith("gsk_"):
        save_api_key(key)
        click.echo(f"{Fore.GREEN}✅ API Key saved successfully to your home directory!")
    else:
        click.echo(f"{Fore.RED}❌ Error: Invalid key format. Groq keys usually start with 'gsk_'.")

@main.command()
def status():
    """Check if the API key is configured."""
    key = load_api_key()
    if key:
        masked_key = f"{key[:7]}...{key[-4:]}"
        click.echo(f"{Fore.GREEN}✅ Status: Configured")
        click.echo(f"{Fore.BLUE}Key: {masked_key}")
    else:
        click.echo(f"{Fore.RED}❌ Status: Not Configured. Run 'mini-claude configure'.")

@main.command()
@click.option('--mode', default='PLAN', help='Start in PLAN or BUILD mode.')
def chat(mode):
    """Step 2: Start the AI coding session."""
    api_key = load_api_key()
    
    if not api_key:
        click.echo(f"{Fore.RED}❌ Error: No API Key found. Please run 'mini-claude configure' first.")
        return

    # Initialize Engine
    engine = OpenCodeEngine(api_key=api_key)
    engine.mode = mode.upper()
    
    click.echo(f"\n{Fore.MAGENTA}{Style.BRIGHT}🚀 Mini-Claude ")
    click.echo(f"{Fore.CYAN}Mode: {engine.mode}")
    click.echo(f"{Fore.YELLOW}Commands: /plan (Think) | /build (Act) | /exit (Quit)\n")

    while True:
        try:
            # Styled Input Prompt
            prompt_color = Fore.GREEN if engine.mode == "BUILD" else Fore.BLUE
            user_input = input(f"{prompt_color}({engine.mode}) > {Style.RESET_ALL}").strip()
            
            if not user_input: 
                continue
            
            # Command Handling
            cmd_lower = user_input.lower()
            if cmd_lower == "/exit":
                click.echo(f"{Fore.YELLOW}Goodbye! 👋")
                break
            elif cmd_lower == "/plan":
                engine.mode = "PLAN"
                click.echo(f"{Fore.BLUE}Switched to PLAN mode. (Observation & Planning)")
                continue
            elif cmd_lower == "/build":
                engine.mode = "BUILD"
                click.echo(f"{Fore.GREEN}Switched to BUILD mode. (Execution & Coding)")
                continue

            # Get AI Response
            click.echo(f"{Style.DIM}Thinking...")
            response = engine.chat(user_input)
            
            # Print AI response in a clear block
            click.echo(f"\n{Fore.WHITE}{Style.BRIGHT}AI: {response}\n")
            
        except KeyboardInterrupt:
            click.echo(f"\n{Fore.YELLOW}Session ended via keyboard.")
            break
        except Exception as e:
            click.echo(f"{Fore.RED}❌ Engine Error: {e}")

if __name__ == "__main__":
    main()