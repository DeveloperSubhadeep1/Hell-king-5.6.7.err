# import logging
# import asyncio
# from pyrogram import Client, filters, enums
# from pyrogram.errors import FloodWait
# from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
# from info import ADMINS, INDEX_REQ_CHANNEL as LOG_CHANNEL
# from database.ia_filterdb import save_file
# from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from utils import temp
# import re
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# lock = asyncio.Lock()


# @Client.on_callback_query(filters.regex(r'^index'))
# async def index_files(bot, query):
#     if query.data.startswith('index_cancel'):
#         temp.CANCEL = True
#         return await query.answer("Cancelling Indexing")
#     _, raju, chat, lst_msg_id, from_user = query.data.split("#")
#     if raju == 'reject':
#         await query.message.delete()
#         await bot.send_message(int(from_user),
#                                f'Your Submission for indexing {chat} has been declined by our moderators.',
#                                reply_to_message_id=int(lst_msg_id))
#         return

#     if lock.locked():
#         return await query.answer('Wait until previous process complete.', show_alert=True)
#     msg = query.message

#     await query.answer('Processing...⏳', show_alert=True)
#     if int(from_user) not in ADMINS:
#         await bot.send_message(int(from_user),
#                                f'Your Submission for indexing {chat} has been accepted by our moderators and will be added soon.',
#                                reply_to_message_id=int(lst_msg_id))
#     await msg.edit(
#         "Starting Indexing",
#         reply_markup=InlineKeyboardMarkup(
#             [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
#         )
#     )
#     try:
#         chat = int(chat)
#     except:
#         chat = chat
#     await index_files_to_db(int(lst_msg_id), chat, msg, bot)


# @Client.on_message((filters.forwarded | (filters.regex(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text ) & filters.private & filters.incoming)
# async def send_for_index(bot, message):
#     if message.text:
#         regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
#         match = regex.match(message.text)
#         if not match:
#             return await message.reply('Invalid link')
#         chat_id = match.group(4)
#         last_msg_id = int(match.group(5))
#         if chat_id.isnumeric():
#             chat_id  = int(("-100" + chat_id))
#     elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
#         last_msg_id = message.forward_from_message_id
#         chat_id = message.forward_from_chat.username or message.forward_from_chat.id
#     else:
#         return
#     try:
#         await bot.get_chat(chat_id)
#     except ChannelInvalid:
#         return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')
#     except (UsernameInvalid, UsernameNotModified):
#         return await message.reply('Invalid Link specified.')
#     except Exception as e:
#         logger.exception(e)
#         return await message.reply(f'Errors - {e}')
#     try:
#         k = await bot.get_messages(chat_id, last_msg_id)
#     except:
#         return await message.reply('Make Sure That Iam An Admin In The Channel, if channel is private')
#     if k.empty:
#         return await message.reply('This may be group and iam not a admin of the group.')

#     if message.from_user.id in ADMINS:
#         buttons = [
#             [InlineKeyboardButton('Yes', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
#             [InlineKeyboardButton('Close', callback_data='close_data')]
#         ]
#         reply_markup = InlineKeyboardMarkup(buttons)
#         return await message.reply(
#             f'Do you Want To Index This Channel/ Group ?\n\nChat ID/ Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>\n\nɴᴇᴇᴅ sᴇᴛsᴋɪᴘ 👉🏻 /setskip',
#             reply_markup=reply_markup)

#     if type(chat_id) is int:
#         try:
#             link = (await bot.create_chat_invite_link(chat_id)).invite_link
#         except ChatAdminRequired:
#             return await message.reply('Make sure I am an admin in the chat and have permission to invite users.')
#     else:
#         link = f"@{message.forward_from_chat.username}"
#     buttons = [
#         [InlineKeyboardButton('Accept Index', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
#         [InlineKeyboardButton('Reject Index', callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}')]
#     ]
#     reply_markup = InlineKeyboardMarkup(buttons)
#     await bot.send_message(LOG_CHANNEL,
#                            f'#IndexRequest\n\nBy : {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID/ Username - <code> {chat_id}</code>\nLast Message ID - <code>{last_msg_id}</code>\nInviteLink - {link}',
#                            reply_markup=reply_markup)
#     await message.reply('ThankYou For the Contribution, Wait For My Moderators to verify the files.')


# @Client.on_message(filters.command('setskip') & filters.user(ADMINS))
# async def set_skip_number(bot, message):
#     if ' ' in message.text:
#         _, skip = message.text.split(" ")
#         try:
#             skip = int(skip)
#         except:
#             return await message.reply("Skip number should be an integer.")
#         await message.reply(f"Successfully set SKIP number as {skip}")
#         temp.CURRENT = int(skip)
#     else:
#         await message.reply("Give me a skip number")


# async def index_files_to_db(lst_msg_id, chat, msg, bot):
#     total_files = 0
#     duplicate = 0
#     errors = 0
#     deleted = 0
#     no_media = 0
#     unsupported = 0
#     async with lock:
#         try:
#             current = temp.CURRENT
#             temp.CANCEL = False
#             async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
#                 if temp.CANCEL:
#                     await msg.edit(f"Successfully Cancelled!!\n\nSaved <code>{total_files}</code> files to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>")
#                     break
#                 current += 1
#                 if current % 100 == 0:
#                     can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
#                     reply = InlineKeyboardMarkup(can)
#                     await msg.edit_text(
#                         text=f"Total messages fetched: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>",
#                         reply_markup=reply)
#                 if message.empty:
#                     deleted += 1
#                     continue
#                 elif not message.media:
#                     no_media += 1
#                     continue
#                 elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
#                     unsupported += 1
#                     continue
#                 media = getattr(message, message.media.value, None)
#                 if not media:
#                     unsupported += 1
#                     continue
#                 media.file_type = message.media.value
#                 media.caption = message.caption
#                 aynav, vnay = await save_file(bot, media)
#                 if aynav:
#                     total_files += 1
#                 elif vnay == 0:
#                     duplicate += 1
#                 elif vnay == 2:
#                     errors += 1
#         except Exception as e:
#             logger.exception(e)
#             await msg.edit(f'Error: {e}')
#         else:
#             await msg.edit(f'Succesfully saved <code>{total_files}</code> to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>')












# import logging
# import asyncio
# import time
# from math import ceil # NEW: Added for batch calculation
# from pyrogram import Client, filters, enums
# from pyrogram.errors import FloodWait
# from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
# from info import ADMINS, INDEX_REQ_CHANNEL as LOG_CHANNEL
# from database.ia_filterdb import save_file # Assuming this function exists and works
# from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# import re
# from utils import temp, get_readable_time # Assuming 'temp' is a storage object like a dict or class with attributes 'CURRENT' and 'CANCEL'

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# lock = asyncio.Lock()

# # --- Utility Function for Progress Bar (Updated to use Emojis) ---

# def get_progress_bar(percent, length=10):
#     """Creates an emoji-based progress bar."""
#     if percent < 0:
#         percent = 0
#     elif percent > 100:
#         percent = 100
        
#     filled = int(length * percent / 100)
#     unfilled = length - filled
#     return '🟩' * filled + '⬜️' * unfilled


# # --- Callback Query Handler ---

# @Client.on_callback_query(filters.regex(r'^index'))
# async def index_files(bot, query):
#     """Handles index-related callback queries (Cancel, Accept, Reject)."""
    
#     # 1. Handle Cancellation
#     if query.data.startswith('index_cancel'):
#         temp.CANCEL = True
#         return await query.answer("Cancelling Indexing", show_alert=True)
    
#     # 2. Parse Data for Accept/Reject
#     # Format: index#action#chat_id#lst_msg_id#from_user
#     try:
#         _, action, chat, lst_msg_id, from_user = query.data.split("#")
#     except ValueError:
#         logger.error(f"Invalid callback data format: {query.data}")
#         return await query.answer("Error processing request.", show_alert=True)

#     # 3. Handle Rejection (Moderator action)
#     if action == 'reject':
#         await query.message.delete()
#         try:
#             await bot.send_message(
#                 int(from_user),
#                 f'Your submission for indexing `{chat}` has been declined by the moderators.',
#                 reply_to_message_id=int(lst_msg_id)
#             )
#         except Exception as e:
#             logger.warning(f"Failed to notify user {from_user} about rejection: {e}")
#         return await query.answer("Indexing request rejected.")

#     # 4. Check Lock for Concurrency
#     if lock.locked():
#         return await query.answer('Wait until the previous process completes.', show_alert=True)
    
#     # 5. Handle Acceptance and Start Indexing
#     msg = query.message
#     await query.answer('Starting Indexing process...⏳', show_alert=True)

#     # Notify the requesting user if they are not an Admin
#     if int(from_user) not in ADMINS:
#         try:
#             await bot.send_message(
#                 int(from_user),
#                 f'Your submission for indexing `{chat}` has been accepted by the moderators and will start soon.',
#                 reply_to_message_id=int(lst_msg_id)
#             )
#         except Exception as e:
#             logger.warning(f"Failed to notify user {from_user} about acceptance: {e}")

#     # Update the moderator's message to show the process is starting
#     await msg.edit(
#         f"Indexing of **{chat}** accepted. Starting process...",
#         reply_markup=InlineKeyboardMarkup(
#             [[InlineKeyboardButton('Cancel Indexing', callback_data='index_cancel')]]
#         ),
#         parse_mode=enums.ParseMode.MARKDOWN
#     )
    
#     # Convert chat to int if it's numeric, otherwise keep as username/string
#     try:
#         chat_id_or_username = int(chat) if str(chat).lstrip('-').isdigit() else chat
#     except ValueError:
#         chat_id_or_username = chat

#     await index_files_to_db(int(lst_msg_id), chat_id_or_username, msg, bot)


# # --- Message Handler (Index Request) ---

# @Client.on_message(
#     (
#         filters.forwarded | 
#         (filters.regex(r"(https?://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$") & filters.text)
#     ) & filters.private & filters.incoming
# )
# async def send_for_index(bot, message):
#     """Handles index requests via forwarded messages or channel links."""
#     chat_id = None
#     last_msg_id = None
    
#     if message.text:
#         # Handle link input
#         regex = re.compile(r"(https?://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
#         match = regex.match(message.text)
#         if not match:
#             return await message.reply('Invalid Telegram channel or group link format.')
            
#         chat_id = match.group(4)
#         last_msg_id = int(match.group(5))
        
#         # Convert public username/ID to Pyrogram standard chat ID format
#         if chat_id.isdigit():
#             chat_id = int(f"-100{chat_id}")
    
#     elif message.forward_from_chat and message.forward_from_chat.type == enums.ChatType.CHANNEL:
#         # Handle forwarded message
#         last_msg_id = message.forward_from_message_id
#         chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    
#     else:
#         # Ignore non-link/non-forwarded messages that somehow pass the filter
#         return await message.reply('Please forward a channel message or provide a channel/group link.')

#     # 1. Validate Chat Access
#     try:
#         chat_info = await bot.get_chat(chat_id)
#         # Check if we can access the last message
#         k = await bot.get_messages(chat_id, last_msg_id)
#         if k.empty:
#             return await message.reply('Could not fetch the last message. Make sure the message ID is correct and I am an admin in the channel/group.')
            
#     except ChannelInvalid:
#         return await message.reply('This may be a private channel/group. Make me an admin there to index the files.')
#     except (UsernameInvalid, UsernameNotModified):
#         return await message.reply('Invalid Link or Username specified.')
#     except Exception as e:
#         logger.exception(f"Error checking chat access for {chat_id}: {e}")
#         return await message.reply(f'An unexpected error occurred during chat validation: `{e}`')

#     # 2. Get Invite Link for Moderator/Log Channel
#     link = ''
#     if chat_info.username:
#         # Use public link if available
#         link = f"@{chat_info.username}"
#     elif isinstance(chat_id, int):
#         try:
#             # Try to create a temporary invite link if it's a private chat ID
#             link = (await bot.create_chat_invite_link(chat_id)).invite_link
#         except ChatAdminRequired:
#             return await message.reply('Make sure I am an admin in the chat and have permission to **invite users** to create an invite link for moderators to verify.')
#         except Exception as e:
#             logger.error(f"Failed to create invite link for {chat_id}: {e}")
#             link = "Invite link generation failed."

#     # 3. Handle Admin vs. Regular User
#     if message.from_user.id in ADMINS:
#         # Admin: Offer immediate start or close
#         admin_buttons = [
#             [InlineKeyboardButton('Start Indexing Now', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
#             [InlineKeyboardButton('Close Request', callback_data='close_data')]
#         ]
#         reply_markup = InlineKeyboardMarkup(admin_buttons)
#         return await message.reply(
#             f'Indexing Request for **{chat_id}** is ready.\n\nStart ID: `{last_msg_id}`. \n\n**Note:** This will proceed without moderator approval.',
#             reply_markup=reply_markup,
#             parse_mode=enums.ParseMode.MARKDOWN
#         )
    
#     else:
#         # Regular User: Send for moderator approval
#         mod_buttons = [
#             [InlineKeyboardButton('Accept Index', callback_data=f'index#accept#{chat_id}#{message.id}#{message.from_user.id}')],
#             [InlineKeyboardButton('Reject Index', callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}')]
#         ]
#         reply_markup = InlineKeyboardMarkup(mod_buttons)
        
#         # Send notification to the log channel
#         await bot.send_message(
#             LOG_CHANNEL,
#             f'#IndexRequest\n\nBy: {message.from_user.mention} (`{message.from_user.id}`)\nChat ID/ Username: `{chat_id}`\nLast Message ID: `{last_msg_id}`\nInvite Link: {link}',
#             reply_markup=reply_markup,
#             parse_mode=enums.ParseMode.MARKDOWN
#         )
        
#         await message.reply('Thank You for the contribution! Your request has been forwarded to our moderators for verification.')


# # --- Command Handler ---

# @Client.on_message(filters.command('setskip') & filters.user(ADMINS))
# async def set_skip_number(bot, message):
#     """Sets the global skip number (temp.CURRENT) for indexing."""
#     if len(message.command) > 1:
#         skip_value = message.command[1]
#         try:
#             skip = int(skip_value)
#         except ValueError:
#             return await message.reply("The skip number must be a whole integer.")
            
#         temp.CURRENT = max(0, skip) # Ensure skip is not negative
#         await message.reply(f"Successfully set the global **SKIP** number as `{temp.CURRENT}`. Indexing will start from message ID **+1** of this number.", parse_mode=enums.ParseMode.MARKDOWN)
#     else:
#         await message.reply(f"Please specify a skip number.\nCurrent skip is: `{temp.CURRENT}`\nUsage: `/setskip 1000`", parse_mode=enums.ParseMode.MARKDOWN)

# # --- Core Indexing Logic (Updated for Batch Processing and ETA) ---

# async def index_files_to_db(lst_msg_id, chat, msg, bot):
#     """The main function to iterate through a chat and save media to the database."""
#     total_files = 0
#     duplicate = 0
#     errors = 0
#     deleted = 0
#     no_media = 0
#     unsupported = 0
#     BATCH_SIZE = 200 # Set a constant batch size
#     start_time = time.time()
    
#     current = temp.CURRENT # Use a local var for the skip point
#     start_id = lst_msg_id

#     async with lock:
#         try:
#             temp.CANCEL = False
            
#             # CRITICAL CHECK: Ensure start ID is greater than the skip point
#             if start_id <= current:
#                 await msg.edit_text(
#                     f"**Indexing Failed!** 🚫\n\nThe starting Message ID (`{start_id}`) is lower than or equal to the current global SKIP number (`{current}`).\n\nUse `/setskip 0` to reset the skip number, or provide a link with a higher message ID.",
#                     parse_mode=enums.ParseMode.MARKDOWN
#                 )
#                 return

#             total_fetch = start_id - current # Total number of IDs to process
#             total_messages_processed = 0
            
#             # The batches need to iterate backwards from lst_msg_id down to current + 1
#             # We determine the number of batches required for this range.
#             batches = ceil(total_fetch / BATCH_SIZE)
#             batch_times = []
            
#             await msg.edit(
#                 f"📊 Indexing Starting......\n"
#                 f"💬 Total Message IDs to cover: <code>{total_fetch}</code>\n"
#                 f"📦 Batches to Process: <code>{batches}</code>\n"
#                 f"⏰ Elapsed: <code>{get_readable_time(time.time() - start_time)}</code>",
#                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]),
#                 parse_mode=enums.ParseMode.HTML
#             )
            
#             # Iterate through the batches
#             for batch in range(batches):
#                 if temp.CANCEL:
#                     break
                    
#                 batch_start = time.time()
                
#                 # Calculate the message IDs for the current batch (reverse order logic)
#                 # The ID range runs from current + 1 up to lst_msg_id.
                
#                 # Start index for this batch (relative to the end)
#                 start_offset = batch * BATCH_SIZE
#                 # End index for this batch (relative to the end)
#                 end_offset = min((batch + 1) * BATCH_SIZE, total_fetch)
                
#                 # Determine the actual message ID range to fetch
#                 # Note: Pyrogram's get_messages takes a list of IDs. We iterate backwards.
                
#                 # The highest ID in the current batch:
#                 high_id = start_id - start_offset
#                 # The lowest ID in the current batch:
#                 low_id = max(current + 1, start_id - end_offset + 1)
                
#                 message_ids = list(range(low_id, high_id + 1))
                
#                 if not message_ids:
#                     break # Should not happen if logic is correct, but safe break
                
#                 try:
#                     # Fetch messages in bulk
#                     messages = await bot.get_messages(chat, message_ids)
#                 except Exception as e:
#                     logger.error(f"Failed to fetch batch {batch+1} in {chat}: {e}")
#                     errors += len(message_ids)
#                     total_messages_processed += len(message_ids)
#                     continue
                    
#                 save_tasks = []
                
#                 # Process fetched messages
#                 for message in messages:
#                     # message can be None if the message ID was deleted
#                     if not message:
#                         deleted += 1
#                         total_messages_processed += 1
#                         continue
                        
#                     try:
#                         if message.empty:
#                             deleted += 1
#                             continue
#                         elif not message.media:
#                             no_media += 1
#                             continue
#                         elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
#                             unsupported += 1
#                             continue
                            
#                         media = getattr(message, message.media.value, None)
#                         if not media:
#                             unsupported += 1
#                             continue
                            
#                         # Prepare media object for saving
#                         media.file_type = message.media.value
#                         media.caption = message.caption
                        
#                         # Fix: Ensure 'bot' is passed to save_file
#                         save_tasks.append(save_file(bot, media)) 

#                     except Exception:
#                         errors += 1
#                         continue
                
#                 # Run database saves concurrently for the current batch
#                 results = await asyncio.gather(*save_tasks, return_exceptions=True)
                
#                 for result in results:
#                     if isinstance(result, Exception):
#                         errors += 1
#                         logger.error(f"Error during save_file: {result}")
#                     else:
#                         ok, code = result
#                         if ok:
#                             total_files += 1
#                         elif code == 0:
#                             duplicate += 1
#                         elif code == 2:
#                             errors += 1
                            
#                 # Update counters and timing
#                 messages_in_batch = len(message_ids)
#                 total_messages_processed += messages_in_batch
#                 batch_time = time.time() - batch_start
#                 batch_times.append(batch_time)
                
#                 elapsed = time.time() - start_time
#                 progress = total_messages_processed
                
#                 # Calculate ETA
#                 percentage = (progress / total_fetch) * 100
#                 avg_batch_time = sum(batch_times) / len(batch_times)
#                 eta = ((total_fetch - progress) / BATCH_SIZE) * avg_batch_time
                
#                 progress_bar_text = get_progress_bar(int(percentage))
                
#                 update_text = (
#                     f"📊 **Indexing Progress** 📦 Batch `{batch + 1}`/`{batches}`\n"
#                     f"{progress_bar_text} <code>{percentage:.1f}%</code>\n\n"
#                     f"**Stats:**\n"
#                     f"Fetched IDs: <code>{progress}</code> / <code>{total_fetch}</code>\n"
#                     f"Files Saved: <code>{total_files}</code>\n"
#                     f"Duplicates: <code>{duplicate}</code>\n"
#                     f"Errors: <code>{errors}</code>\n"
#                     f"Skipped Non-Media/Deleted: <code>{deleted + no_media + unsupported}</code>\n"
#                     f"⏱️ Elapsed: <code>{get_readable_time(elapsed)}</code>\n"
#                     f"⏰ ETA: <code>{get_readable_time(eta)}</code>"
#                 )
                
#                 can_button = [[InlineKeyboardButton('Cancel Indexing', callback_data='index_cancel')]]
#                 await msg.edit_text(text=update_text, reply_markup=InlineKeyboardMarkup(can_button), parse_mode=enums.ParseMode.HTML)
            
#         except FloodWait as e:
#             logger.warning(f"Hit FloodWait for {e.value} seconds.")
#             await msg.edit_text(f"FloodWait encountered. Waiting for `{e.value}` seconds...", parse_mode=enums.ParseMode.MARKDOWN)
#             await asyncio.sleep(e.value + 5)
            
#         except Exception as e:
#             logger.exception(f"Fatal error during indexing of chat {chat}: {e}")
#             await msg.edit_text(f'Indexing stopped due to a fatal error: <code>{e}</code>', parse_mode=enums.ParseMode.HTML)
            
#         finally:
#             temp.CANCEL = False # Reset cancel flag
            
#             # Final summary message
#             final_elapsed = time.time() - start_time
            
#             final_text = (
#                 f'✅ **Indexing Completed!**\n\n'
#                 f'Time taken: <code>{get_readable_time(final_elapsed)}</code>\n\n'
#                 f'**Summary:**\n'
#                 f'Files Saved: <code>{total_files}</code>\n'
#                 f'Duplicate Files Skipped: <code>{duplicate}</code>\n'
#                 f'Deleted Messages Skipped: <code>{deleted}</code>\n'
#                 f'Non-Media Messages Skipped: <code>{no_media + unsupported}</code>\n'
#                 f'Errors Occurred: <code>{errors}</code>'
#             )
            
#             # Only send the final summary if we successfully indexed anything or finished normally
#             if start_id > current and not temp.CANCEL:
#                 await msg.edit_text(final_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Close', callback_data='close_data')]]), parse_mode=enums.ParseMode.HTML)



# import logging
# import asyncio
# import time # Added for sleep in progress_for_pyrogram
# from pyrogram import Client, filters, enums
# from pyrogram.errors import FloodWait, MessageNotModified # Added MessageNotModified for progress bar updates
# from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
# from info import ADMINS, INDEX_REQ_CHANNEL as LOG_CHANNEL
# from database.ia_filterdb import save_file
# from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from utils import temp # Assuming temp is a module or object with 'CANCEL' and 'CURRENT'
# import re
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# lock = asyncio.Lock()

# # --- Placeholder for a simplified progress bar utility ---

# # NOTE: This is a simplified, synchronous version. 
# # A real-world version should handle threading/async better.
# async def progress_for_pyrogram(
#     current,
#     total,
#     ud_type,
#     message,
#     start
# ):
#     """
#     Shows a simple progress bar in a Telegram message.
#     """
#     now = time.time()
#     diff = now - start
    
#     # Update every 5 seconds or if the operation is complete
#     if round(diff % 5) == 0 or current == total:
#         percentage = current * 100 / total
        
#         # Simple text progress bar
#         bar_len = 20
#         filled_len = int(bar_len * percentage // 100)
#         bar = '█' * filled_len + '░' * (bar_len - filled_len)
        
#         text = f"**{ud_type}**\n"
#         text += f"```\n{bar} {percentage:.2f}%\n```\n"
#         text += f"**Processed:** `{current}` / `{total}`\n"
#         text += f"**Time Elapsed:** `{round(diff)}s`"
        
#         try:
#             await message.edit_text(text)
#         except MessageNotModified:
#             pass # Ignore if the message content hasn't changed enough

# # You would ideally put this in `utils.py` and import it.
# # For this example, I've put it here for completeness.

# # -------------------------------------------------------------------


# @Client.on_callback_query(filters.regex(r'^index'))
# async def index_files(bot, query):
#     if query.data.startswith('index_cancel'):
#         temp.CANCEL = True
#         # Allow cancelling immediately
#         await query.answer("Cancelling Indexing", show_alert=True)
#         return
        
#     _, raju, chat, lst_msg_id, from_user = query.data.split("#")
#     if raju == 'reject':
#         await query.message.delete()
#         await bot.send_message(int(from_user),
#                                f'Your Submission for indexing {chat} has been **declined** by our moderators.',
#                                reply_to_message_id=int(lst_msg_id))
#         return

#     if lock.locked():
#         return await query.answer('Wait until previous process complete.', show_alert=True)
#     msg = query.message

#     await query.answer('Starting Indexing... ⏳', show_alert=True)
#     if int(from_user) not in ADMINS:
#         await bot.send_message(int(from_user),
#                                f'Your Submission for indexing {chat} has been **accepted** by our moderators and will be added soon.',
#                                reply_to_message_id=int(lst_msg_id))
    
#     # Edit the message to show it's starting, preparing for the progress bar
#     await msg.edit(
#         "**Starting Indexing...** Getting chat history count.",
#         reply_markup=InlineKeyboardMarkup(
#             [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
#         )
#     )
    
#     try:
#         chat = int(chat)
#     except ValueError:
#         pass # Keep as string if it's a username
        
#     # Start the indexing process
#     await index_files_to_db(int(lst_msg_id), chat, msg, bot)


# @Client.on_message((filters.forwarded | (filters.regex(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text ) & filters.private & filters.incoming)
# async def send_for_index(bot, message):
#     # This function remains largely unchanged as its role is to initiate indexing
#     # and request approval, not to handle the indexing progress itself.
#     if message.text:
#         regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
#         match = regex.match(message.text)
#         if not match:
#             return await message.reply('Invalid link')
#         chat_id = match.group(4)
#         last_msg_id = int(match.group(5))
#         if chat_id.isnumeric():
#             chat_id = int(("-100" + chat_id))
#     elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
#         last_msg_id = message.forward_from_message_id
#         chat_id = message.forward_from_chat.username or message.forward_from_chat.id
#     else:
#         return
        
#     try:
#         await bot.get_chat(chat_id)
#     except ChannelInvalid:
#         return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')
#     except (UsernameInvalid, UsernameNotModified):
#         return await message.reply('Invalid Link specified.')
#     except Exception as e:
#         logger.exception(e)
#         return await message.reply(f'Errors - {e}')
    
#     try:
#         k = await bot.get_messages(chat_id, last_msg_id)
#     except:
#         return await message.reply('Make Sure That Iam An Admin In The Channel, if channel is private')
        
#     if k.empty:
#         return await message.reply('This may be group and I am not an admin of the group.')

#     if message.from_user.id in ADMINS:
#         buttons = [
#             [InlineKeyboardButton('Yes', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
#             [InlineKeyboardButton('Close', callback_data='close_data')]
#         ]
#         reply_markup = InlineKeyboardMarkup(buttons)
#         return await message.reply(
#             f'Do you Want To Index This Channel/ Group ?\n\nChat ID/ Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>\n\nɴᴇᴇᴅ sᴇᴛsᴋɪᴘ 👉🏻 /setskip',
#             reply_markup=reply_markup)

#     if type(chat_id) is int:
#         try:
#             link = (await bot.create_chat_invite_link(chat_id)).invite_link
#         except ChatAdminRequired:
#             return await message.reply('Make sure I am an admin in the chat and have permission to invite users.')
#     else:
#         link = f"@{chat_id}" # Use chat_id which is the username here
        
#     buttons = [
#         [InlineKeyboardButton('Accept Index', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
#         [InlineKeyboardButton('Reject Index', callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}')]
#     ]
#     reply_markup = InlineKeyboardMarkup(buttons)
#     await bot.send_message(LOG_CHANNEL,
#                            f'#IndexRequest\n\nBy : {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID/ Username - <code> {chat_id}</code>\nLast Message ID - <code>{last_msg_id}</code>\nInviteLink - {link}',
#                            reply_markup=reply_markup)
#     await message.reply('ThankYou For the Contribution, Wait For My Moderators to verify the files.')


# @Client.on_message(filters.command('setskip') & filters.user(ADMINS))
# async def set_skip_number(bot, message):
#     if ' ' in message.text:
#         _, skip = message.text.split(" ")
#         try:
#             skip = int(skip)
#         except ValueError:
#             return await message.reply("Skip number should be an integer.")
#         await message.reply(f"Successfully set **SKIP** number as **{skip}**")
#         temp.CURRENT = int(skip)
#     else:
#         await message.reply("Give me a skip number (e.g., `/setskip 100`)")

# # --- Improved Indexing Function with Progress Bar ---

# async def index_files_to_db(lst_msg_id, chat, msg, bot):
#     total_files = 0
#     duplicate = 0
#     errors = 0
#     deleted = 0
#     no_media = 0
#     unsupported = 0
    
#     # 1. Get the total message count for the progress bar
#     try:
#         # Get the total history count up to lst_msg_id
#         # Note: bot.get_chat_history_count() gets the total history.
#         # It's an approximation, but better than nothing.
#         total_messages = await bot.get_chat_history_count(chat)
#         # We only care about messages from 'temp.CURRENT' (the skip number) up to 'lst_msg_id'
#         start_id = temp.CURRENT if hasattr(temp, 'CURRENT') else 0
#         total_to_process = lst_msg_id - start_id
        
#         # If the channel is small or lst_msg_id is much less than total_messages, 
#         # use the calculated value. Otherwise, use total_messages as a safe upper bound.
#         # Using a simple check to prevent negative or zero total count
#         if total_to_process <= 0:
#             total_to_process = total_messages
            
#     except Exception as e:
#         logger.warning(f"Could not get chat history count: {e}")
#         total_to_process = 0 # Fallback to unknown total

#     current_processed = 0
#     start_time = time.time() # Start time for progress calculation

#     async with lock:
#         try:
#             current = temp.CURRENT if hasattr(temp, 'CURRENT') else 0
#             temp.CANCEL = False
            
#             # Use iter_messages with a high limit if total_to_process is unknown
#             async for message in bot.iter_messages(chat, lst_msg_id, current):
#                 if temp.CANCEL:
#                     await msg.edit(
#                         f"**Indexing Cancelled!** ⚠️\n\n"
#                         f"**Saved Files:** <code>{total_files}</code>\n"
#                         f"**Skipped (Duplicate):** <code>{duplicate}</code>\n"
#                         f"**Skipped (Deleted):** <code>{deleted}</code>\n"
#                         f"**Skipped (No/Unsupported Media):** <code>{no_media + unsupported}</code>\n"
#                         f"**Errors:** <code>{errors}</code>"
#                     )
#                     break
                
#                 current += 1
#                 current_processed += 1
                
#                 # 2. Update the progress bar periodically
#                 if current_processed % 50 == 0 or current_processed == total_to_process:
#                     # Update message in background without interrupting the loop
#                     if total_to_process > 0:
#                         await progress_for_pyrogram(
#                             current_processed,
#                             total_to_process,
#                             f"Indexing **{chat}**...",
#                             msg,
#                             start_time
#                         )
#                     else:
#                         # Fallback for unknown total
#                         can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
#                         reply = InlineKeyboardMarkup(can)
#                         await msg.edit_text(
#                             text=f"**Indexing in Progress...**\n"
#                                 f"Total messages fetched: <code>{current}</code>\n"
#                                 f"Total files saved: <code>{total_files}</code>\n"
#                                 f"Skipped: <code>{duplicate}</code> (Duplicate) / <code>{deleted}</code> (Deleted) / <code>{no_media + unsupported}</code> (No/Unsupported Media)\n"
#                                 f"Errors Occurred: <code>{errors}</code>",
#                             reply_markup=reply
#                         )
#                     # Introduce a small delay to avoid hitting FloodWait from rapid message edits
#                     await asyncio.sleep(1) 

#                 if message.empty:
#                     deleted += 1
#                     continue
#                 elif not message.media:
#                     no_media += 1
#                     continue
#                 elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
#                     unsupported += 1
#                     continue
                    
#                 media = getattr(message, message.media.value, None)
#                 if not media:
#                     unsupported += 1
#                     continue
                    
#                 media.file_type = message.media.value
#                 media.caption = message.caption
                
#                 # Assuming save_file returns (success_bool, status_code)
#                 # status_code: 1=saved, 0=duplicate, 2=error
#                 aynav, vnay = await save_file(bot, media)
                
#                 if aynav:
#                     total_files += 1
#                 elif vnay == 0:
#                     duplicate += 1
#                 elif vnay == 2:
#                     errors += 1
                    
#         except FloodWait as e:
#             # Handle FloodWait errors by waiting and logging
#             logger.warning(f"Hit FloodWait: sleeping for {e.value} seconds")
#             await asyncio.sleep(e.value)
#         except Exception as e:
#             logger.exception(e)
#             await msg.edit(f'**An Unexpected Error Occurred:** `{e}`')
            
#         else:
#             # Final message upon completion
#             await msg.edit(
#                 f'**Indexing Complete!** ✅\n\n'
#                 f'Successfully saved **<code>{total_files}</code>** files to dataBase!\n'
#                 f'**Skipped (Duplicate):** <code>{duplicate}</code>\n'
#                 f'**Skipped (Deleted):** <code>{deleted}</code>\n'
#                 f'**Skipped (No/Unsupported Media):** <code>{no_media + unsupported}</code>\n'
#                 f'**Errors Occurred:** <code>{errors}</code>'
#             )
            
# # -------------------------------------------------------------------




















import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import ADMINS, INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file # Assuming this function exists and works
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import time
from utils import temp, get_readable_time # Assuming 'temp' is a storage object like a dict or class with attributes 'CURRENT' and 'CANCEL'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()

# --- Utility Function for Progress Bar ---

def progress_bar(current, total):
    """Generates a text-based progress bar."""
    if total <= 0:
        return "`[....................]` 0.0%"
        
    # Bar length fixed to 20 characters
    bar_length = 20
    # Calculate percentage
    percent = current / total
    # Calculate filled length
    filled_length = int(bar_length * percent)
    
    # Create the bar string using blocks and dots
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    # Return formatted string with percentage
    return f"`[{bar}]` {percent:.1%}"


# --- Callback Query Handler ---

@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    """Handles index-related callback queries (Cancel, Accept, Reject)."""
    
    # 1. Handle Cancellation
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing", show_alert=True)
    
    # 2. Parse Data for Accept/Reject
    # Format: index#action#chat_id#lst_msg_id#from_user
    try:
        _, action, chat, lst_msg_id, from_user = query.data.split("#")
    except ValueError:
        logger.error(f"Invalid callback data format: {query.data}")
        return await query.answer("Error processing request.", show_alert=True)

    # 3. Handle Rejection (Moderator action)
    if action == 'reject':
        await query.message.delete()
        try:
            await bot.send_message(
                int(from_user),
                f'Your submission for indexing `{chat}` has been declined by the moderators.',
                reply_to_message_id=int(lst_msg_id) # Use lst_msg_id as it often refers to the *user's original request message ID*
            )
        except Exception as e:
            logger.warning(f"Failed to notify user {from_user} about rejection: {e}")
        return await query.answer("Indexing request rejected.")

    # 4. Check Lock for Concurrency
    if lock.locked():
        return await query.answer('Wait until the previous process completes.', show_alert=True)
    
    # 5. Handle Acceptance and Start Indexing
    msg = query.message
    await query.answer('Starting Indexing process...⏳', show_alert=True)

    # Notify the requesting user if they are not an Admin (Admins are self-notified via the bot response)
    if int(from_user) not in ADMINS:
        try:
            await bot.send_message(
                int(from_user),
                f'Your submission for indexing `{chat}` has been accepted by the moderators and will start soon.',
                reply_to_message_id=int(lst_msg_id)
            )
        except Exception as e:
            logger.warning(f"Failed to notify user {from_user} about acceptance: {e}")

    # Update the moderator's message to show the process is starting
    await msg.edit(
        f"Indexing of **{chat}** accepted. Starting process...",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Cancel Indexing', callback_data='index_cancel')]]
        ),
        parse_mode=enums.ParseMode.MARKDOWN
    )
    
    # Convert chat to int if it's numeric, otherwise keep as username/string
    try:
        chat_id_or_username = int(chat) if str(chat).lstrip('-').isdigit() else chat
    except ValueError:
        chat_id_or_username = chat

    await index_files_to_db(int(lst_msg_id), chat_id_or_username, msg, bot)


# --- Message Handler (Index Request) ---

@Client.on_message(
    (
        filters.forwarded | 
        (filters.regex(r"(https?://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$") & filters.text)
    ) & filters.private & filters.incoming
)
async def send_for_index(bot, message):
    """Handles index requests via forwarded messages or channel links."""
    chat_id = None
    last_msg_id = None
    
    if message.text:
        # Handle link input
        regex = re.compile(r"(https?://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply('Invalid Telegram channel or group link format.')
            
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        
        # Convert public username/ID to Pyrogram standard chat ID format
        if chat_id.isdigit():
            chat_id = int(f"-100{chat_id}")
    
    elif message.forward_from_chat and message.forward_from_chat.type == enums.ChatType.CHANNEL:
        # Handle forwarded message
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    
    else:
        # Ignore non-link/non-forwarded messages that somehow pass the filter
        return await message.reply('Please forward a channel message or provide a channel/group link.')

    # 1. Validate Chat Access
    try:
        chat_info = await bot.get_chat(chat_id)
        # Check if we can access the last message
        k = await bot.get_messages(chat_id, last_msg_id)
        if k.empty:
            return await message.reply('Could not fetch the last message. Make sure the message ID is correct and I am an admin in the channel/group.')
            
    except ChannelInvalid:
        return await message.reply('This may be a private channel/group. Make me an admin there to index the files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link or Username specified.')
    except Exception as e:
        logger.exception(f"Error checking chat access for {chat_id}: {e}")
        return await message.reply(f'An unexpected error occurred during chat validation: `{e}`')

    # 2. Get Invite Link for Moderator/Log Channel
    link = ''
    if chat_info.username:
        # Use public link if available
        link = f"@{chat_info.username}"
    elif isinstance(chat_id, int):
        try:
            # Try to create a temporary invite link if it's a private chat ID
            link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply('Make sure I am an admin in the chat and have permission to **invite users** to create an invite link for moderators to verify.')
        except Exception as e:
            logger.error(f"Failed to create invite link for {chat_id}: {e}")
            link = "Invite link generation failed."

    # 3. Handle Admin vs. Regular User
    if message.from_user.id in ADMINS:
        # Admin: Offer immediate start or close
        admin_buttons = [
            [InlineKeyboardButton('Start Indexing Now', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
            [InlineKeyboardButton('Close Request', callback_data='close_data')]
        ]
        reply_markup = InlineKeyboardMarkup(admin_buttons)
        return await message.reply(
            f'Indexing Request for **{chat_id}** is ready.\n\nStart ID: `{last_msg_id}`. \n\n**Note:** This will proceed without moderator approval.',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    else:
        # Regular User: Send for moderator approval
        mod_buttons = [
            [InlineKeyboardButton('Accept Index', callback_data=f'index#accept#{chat_id}#{message.id}#{message.from_user.id}')],
            [InlineKeyboardButton('Reject Index', callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}')]
        ]
        reply_markup = InlineKeyboardMarkup(mod_buttons)
        
        # Send notification to the log channel
        await bot.send_message(
            LOG_CHANNEL,
            f'#IndexRequest\n\nBy: {message.from_user.mention} (`{message.from_user.id}`)\nChat ID/ Username: `{chat_id}`\nLast Message ID: `{last_msg_id}`\nInvite Link: {link}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
        await message.reply('Thank You for the contribution! Your request has been forwarded to our moderators for verification.')


# --- Command Handler ---

@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    """Sets the global skip number (temp.CURRENT) for indexing."""
    if len(message.command) > 1:
        skip_value = message.command[1]
        try:
            skip = int(skip_value)
        except ValueError:
            return await message.reply("The skip number must be a whole integer.")
            
        temp.CURRENT = max(0, skip) # Ensure skip is not negative
        await message.reply(f"Successfully set the global **SKIP** number as `{temp.CURRENT}`. Indexing will start from message ID **+1** of this number.", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await message.reply(f"Please specify a skip number.\nCurrent skip is: `{temp.CURRENT}`\nUsage: `/setskip 1000`", parse_mode=enums.ParseMode.MARKDOWN)

# --- Core Indexing Logic ---

async def index_files_to_db(lst_msg_id, chat, msg, bot):
    """The main function to iterate through a chat and save media to the database."""
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    current_msg_count = 0 # Messages processed since the start of this index run
    
    # The starting message ID is the last message ID the user requested.
    start_id = lst_msg_id
    
    # NEW: Check if the start ID is less than or equal to the skip point.
    if start_id <= temp.CURRENT:
        await msg.edit_text(
            f"**Indexing Failed!** 🚫\n\nThe starting Message ID (`{start_id}`) is lower than or equal to the current global SKIP number (`{temp.CURRENT}`).\n\nPlease use the `/setskip 0` command to reset the skip number, or provide a link with a higher message ID.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    
    # Calculate approximate total messages to index. 
    # This assumes sequential IDs, which is why it's an "approximate" total.
    total_to_index = start_id - temp.CURRENT 
    
    start_time = time.time()
    
    async with lock:
        try:
            temp.CANCEL = False
            
            async for message in bot.iter_messages(chat, offset=start_id, reverse=True):
                
                # Check for cancellation requested by the user
                if temp.CANCEL:
                    break
                
                # Stop if we hit the manually set skip point
                if message.id <= temp.CURRENT:
                    logger.info(f"Reached skip point: {temp.CURRENT}")
                    break
                
                current_msg_count += 1
                
                # Update status message every 80 messages
                if current_msg_count % 80 == 0:
                    elapsed = time.time() - start_time
                    speed = current_msg_count / elapsed
                    
                    # Generate progress bar
                    bar = progress_bar(current_msg_count, total_to_index)

                    update_text = (
                        f"**Indexing Status**\n"
                        f"{bar}\n\n"
                        f"Time: `{get_readable_time(elapsed)}` | Speed: `{speed:.2f} msg/s`\n"
                        f"Total messages fetched: `{current_msg_count}` (Up to ID: `{message.id}`)\n"
                        f"Approx. Total to Index: `{total_to_index}`\n"
                        f"Files Saved: `{total_files}`\n"
                        f"Skipped:\n"
                        f"  - Duplicate: `{duplicate}`\n"
                        f"  - Deleted: `{deleted}`\n"
                        f"  - No/Unsupported Media: `{no_media + unsupported}`\n"
                        f"Errors: `{errors}`"
                    )
                    can_button = [[InlineKeyboardButton('Cancel Indexing', callback_data='index_cancel')]]
                    await msg.edit_text(text=update_text, reply_markup=InlineKeyboardMarkup(can_button), parse_mode=enums.ParseMode.MARKDOWN)

                # Skip empty (deleted) messages
                if message.empty:
                    deleted += 1
                    continue
                
                # Filter for desired media types
                if not message.media:
                    no_media += 1
                    continue
                
                supported_media = [
                    enums.MessageMediaType.VIDEO, 
                    enums.MessageMediaType.AUDIO, 
                    enums.MessageMediaType.DOCUMENT
                ]
                
                if message.media not in supported_media:
                    unsupported += 1
                    continue

                # Get the media object (video, audio, or document)
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                    
                # Prepare media object for saving
                media.file_type = message.media.value
                media.caption = message.caption
                
                # Save file to database
                # Assuming save_file returns (success_bool, status_code)
                # status_code: 1=saved, 0=duplicate, 2=error
                # FIX: Removed the 'bot' argument from save_file as it is likely causing a TypeError
                # in the database handling function. It should only need the media object.
                success, status_code = await save_file(media)
                
                if success:
                    total_files += 1
                elif status_code == 0: # Duplicate file
                    duplicate += 1
                elif status_code == 2: # Error during saving
                    errors += 1
                
        except FloodWait as e:
            # Handle Pyrogram FloodWait error gracefully
            logger.warning(f"Hit FloodWait for {e.value} seconds.")
            await msg.edit_text(f"FloodWait encountered. Waiting for `{e.value}` seconds...", parse_mode=enums.ParseMode.MARKDOWN)
            await asyncio.sleep(e.value + 5)
            
        except Exception as e:
            logger.exception(f"Fatal error during indexing of chat {chat}: {e}")
            await msg.edit_text(f'Indexing stopped due to a fatal error: `{e}`', parse_mode=enums.ParseMode.MARKDOWN)
            
        finally:
            # Final summary message
            final_elapsed = time.time() - start_time
            
            final_text = (
                f'Indexing process finished!\n'
                f'Time taken: `{get_readable_time(final_elapsed)}`\n\n'
                f'**Summary:**\n'
                f'Files Saved: `{total_files}`\n'
                f'Duplicate Files Skipped: `{duplicate}`\n'
                f'Deleted Messages Skipped: `{deleted}`\n'
                f'Non-Media messages skipped: `{no_media + unsupported}`\n'
                f'Errors Occurred: `{errors}`'
            )
            # Only send the final summary if we didn't exit early due to the skip error
            if start_id > temp.CURRENT:
                await msg.edit_text(final_text, parse_mode=enums.ParseMode.MARKDOWN)
            
            temp.CANCEL = False # Reset cancel flag
