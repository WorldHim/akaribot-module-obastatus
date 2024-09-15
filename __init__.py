from core.builtins import Bot, Image, Plain
from core.component import module
from core.utils.http import get_url

from datetime import datetime

obastatus = module(
    bind_prefix='obastatus',
    desc='{obastatus.help.desc}',
    alias='oba',
    developers=['WorldHim'],
    support_languages=['zh_cn'],
)

def sizeConvert(value):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = 1024.0
    for i in range(len(units)):
        if(value / size) < 1:
            return '%.2f%s' % (value, ' ' + units[i])
        value /= size

async def latestVersion():
    version = await get_url('https://bd.bangbang93.com/openbmclapi/metric/version',
                            fmt='json')
    return f'''{version['version']}@{version['_resolved'].split('#')[1][:7]}'''

@obastatus.command('{{obastatus.help.status}}')
@obastatus.command('status {{obastatus.help.status}}')
async def status(msg: Bot.MessageSession):
    dashboard = await get_url('https://bd.bangbang93.com/openbmclapi/metric/dashboard',
                              fmt='json')

    message = f'''{msg.locale.t('obastatus.message.status',
                                currentNodes = dashboard['currentNodes'],
                                load = round(dashboard['load'] * 100, 2),
                                bandwidth = dashboard['bandwidth'],
                                currentBandwidth = round(dashboard['currentBandwidth'], 2),
                                hits = dashboard['hits'],
                                size = sizeConvert(dashboard['bytes']))}
{msg.locale.t('obastatus.message.queryTime', queryTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}'''

    await msg.finish(message)

@obastatus.command('rank [<rank>] {{obastatus.help.rank}}')
async def rank(msg: Bot.MessageSession, rank: int = 1):
    rankList = await get_url('https://bd.bangbang93.com/openbmclapi/metric/rank',
                             fmt='json')
    cluster = rankList[rank - 1]

    message = f'''{msg.locale.t('obastatus.message.cluster',
                                name = cluster['name'],
                                id = cluster['_id'],
                                hits = cluster['metric']['hits'],
                                size = sizeConvert(cluster['metric']['bytes']))}
{msg.locale.t('obastatus.message.queryTime', queryTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}'''

    try:
        sponsor = cluster['sponsor']
    except KeyError:
        await msg.finish(message)
    else:
        await msg.send_message(message)

        message = msg.locale.t('obastatus.message.sponsor',
                               name = sponsor['name'],
                               url = sponsor['url'])

        try:
            await msg.finish([Plain(message), Image(str(sponsor['banner']))])
        except Exception:
            await msg.finish(message)

@obastatus.command('top [<rank>] {{obastatus.help.top}}')
async def top(msg: Bot.MessageSession, rank: int = 10):
    rankList = await get_url('https://bd.bangbang93.com/openbmclapi/metric/rank',
                             fmt='json')

    cluster = rankList[0]

    try:
        sponsor_name = cluster['sponsor']['name']
    except KeyError:
        sponsor_name = "未知"
    message = msg.locale.t('obastatus.message.top',
                           rank = 1,
                           name = cluster['name'],
                           id = cluster['_id'],
                           hits = cluster['metric']['hits'],
                           size = sizeConvert(cluster['metric']['bytes']),
                           sponsor_name = sponsor_name)

    for i in range(1, rank):
        message += '\n'

        cluster = rankList[i]

        try:
            sponsor_name = cluster['sponsor']['name']
        except KeyError:
            sponsor_name = "未知"

        try:
            message += msg.locale.t('obastatus.message.top',
                                    rank = i + 1,
                                    name = cluster['name'],
                                    id = cluster['_id'],
                                    hits = cluster['metric']['hits'],
                                    size = sizeConvert(cluster['metric']['bytes']),
                                    sponsor_name = sponsor_name)
        except KeyError:
            break

    await msg.send_message(message)

@obastatus.command('version {{obastatus.help.version}}')
async def version(msg: Bot.MessageSession):
    await msg.finish(msg.locale.t('obastatus.message.version', version = await latestVersion()))