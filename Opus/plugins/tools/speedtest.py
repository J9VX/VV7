import asyncio
import speedtest
from pyrogram import filters
from pyrogram.types import Message
from speedtest import ConfigRetrievalError, Speedtest

from Opus import app
from Opus.misc import SUDOERS
from Opus.utils.decorators.language import language

def get_readable_file_size(size_in_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"

async def run_speedtest(m: Message):
    try:
        st = Speedtest()
        await m.edit_text("<i>Finding best server...</i>")
        st.get_best_server()
        
        await m.edit_text("<i>Testing download speed...</i>")
        st.download()
        
        await m.edit_text("<i>Testing upload speed...</i>")
        st.upload()
        
        results = st.results.dict()
        return results, None
        
    except ConfigRetrievalError:
        return None, "Unable to connect to servers to test latency."
    except Exception as e:
        return None, f"Error: {str(e)}"

@app.on_message(filters.command(["speedtest", "spt"]) & SUDOERS)
@language
async def speedtest_command(client, message: Message, _):
    m = await message.reply_text("<i>Starting speedtest...</i>")
    
    results, error = await run_speedtest(m)
    
    if error:
        await m.edit_text(error)
        return
    
    try:
        string_speed = f"""
➲ <b><i>SPEEDTEST INFO</i></b>
┠ <b>Upload:</b> <code>{get_readable_file_size(results['upload'] / 8)}/s</code>
┠ <b>Download:</b> <code>{get_readable_file_size(results['download'] / 8)}/s</code>
┠ <b>Ping:</b> <code>{results['ping']} ms</code>
┠ <b>Time:</b> <code>{results['timestamp']}</code>
┠ <b>Data Sent:</b> <code>{get_readable_file_size(int(results['bytes_sent']))}</code>
┖ <b>Data Received:</b> <code>{get_readable_file_size(int(results['bytes_received']))}</code>

➲ <b><i>SPEEDTEST SERVER</i></b>
┠ <b>Name:</b> <code>{results['server']['name']}</code>
┠ <b>Country:</b> <code>{results['server']['country']}, {results['server']['cc']}</code>
┠ <b>Sponsor:</b> <code>{results['server']['sponsor']}</code>
┠ <b>Latency:</b> <code>{results['server']['latency']}</code>
┠ <b>Latitude:</b> <code>{results['server']['lat']}</code>
┖ <b>Longitude:</b> <code>{results['server']['lon']}</code>

➲ <b><i>CLIENT DETAILS</i></b>
┠ <b>IP Address:</b> <code>{results['client']['ip']}</code>
┠ <b>Latitude:</b> <code>{results['client']['lat']}</code>
┠ <b>Longitude:</b> <code>{results['client']['lon']}</code>
┠ <b>Country:</b> <code>{results['client']['country']}</code>
┠ <b>ISP:</b> <code>{results['client']['isp']}</code>
┖ <b>ISP Rating:</b> <code>{results['client']['isprating']}</code>
"""
        await m.edit_text(string_speed)
        
    except Exception as e:
        await m.edit_text(f"Error processing results: {str(e)}")
