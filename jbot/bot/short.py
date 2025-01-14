from telethon import events, Button
from .utils import split_list, press_event, cmd
from asyncio import exceptions
from .. import jdbot, chat_id, SHORTCUT_FILE, logger, BOT_SET, ch_name


@jdbot.on(events.NewMessage(chats=chat_id, pattern=r'^/a$'))
async def my_a(event):
    markup = []
    SENDER = event.sender_id
    msg = await jdbot.send_message(chat_id, '正在查询您的常用命令，请稍后')
    with open(SHORTCUT_FILE, 'r', encoding='utf-8') as f:
        shortcuts = f.readlines()
    try:
        cmdtext = None

        cmds = {shortcut.split(
                '-->')[0]: shortcut.split('-->')[-1] for shortcut in shortcuts if '-->' in shortcut}

        async with jdbot.conversation(SENDER, timeout=60) as conv:
            markup = [Button.inline(c, data=c) for c in cmds]
            markup = split_list(markup, 3)
            markup.append([Button.inline('取消', data='cancel')])
            msg = await jdbot.edit_message(msg, '请做出您的选择：', buttons=markup)
            convdata = await conv.wait_event(press_event(SENDER))
            res = bytes.decode(convdata.data)
            logger.info(res)
            if res == 'cancel':
                msg = await jdbot.edit_message(msg, '对话已取消')
                conv.cancel()
            else:
                await jdbot.delete_messages(chat_id, msg)
                cmdtext = cmds[res]
                conv.cancel()
        if cmdtext:
            await cmd(cmdtext.replace('nohup ', ''))
    except exceptions.TimeoutError:
        msg = await jdbot.edit_message(msg, '选择已超时，对话已停止')
    except Exception as e:
        await jdbot.edit_message(msg, f'something wrong,I\'m sorry\n{str(e)}')
        logger.error(f'something wrong,I\'m sorry\n{str(e)}', exc_info=1)




@jdbot.on(events.NewMessage(chats=chat_id, pattern=r'^/clearboard'))
async def my_clear(event):
    try:
        await jdbot.send_message(chat_id, '已清空您的keyboard',buttons=Button.clear())
    except Exception as e:
        await jdbot.send_message(chat_id, f'something wrong,I\'m sorry\n{str(e)}')
        logger.error(f'something wrong,I\'m sorry\n{str(e)}')

if ch_name:
    jdbot.add_event_handler(my_a, events.NewMessage(
        from_users=chat_id, pattern=BOT_SET['命令别名']['a']))
