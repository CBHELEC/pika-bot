CURRENCY_API_KEY = 'i almost forgot to censor this uwu'
CURRENCY_API_URL = 'https://v6.exchangerate-api.com/v6/'
@bot.command()
async def convert(ctx, amount: float, from_currency: str, to_currency: str):
    """Convert an amount from one currency to another."""
    response = requests.get(f'{CURRENCY_API_URL}{CURRENCY_API_KEY}/latest/{from_currency.upper()}')
    
    if response.status_code != 200:
        await ctx.send("Error fetching exchange rates. Please try again later.")
        return
    
    data = response.json()
    
    if 'conversion_rates' not in data:
        await ctx.send("Invalid currency code. Please provide valid currency codes.")
        return
    
    conversion_rate = data['conversion_rates'].get(to_currency.upper())
    
    if conversion_rate is None:
        await ctx.send("Invalid target currency code. Please provide a valid target currency code.")
        return
    
    converted_amount = amount * conversion_rate
    
    await ctx.send(f"{amount} {from_currency.upper()} is approximately {converted_amount:.2f} {to_currency.upper()}.")
