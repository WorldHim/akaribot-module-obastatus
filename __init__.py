from core.builtins import Bot
from core.component import module
from core.utils.http import get_url

obastatus = module(
    bind_prefix='obastatus',
    desc='{obastatus.help.desc}',
    alias='oba',
    developers=['WorldHim'],
    support_languages=['zh_cn'],
)

async def latestVersion():
    result = await get_url('https://bd.bangbang93.com/openbmclapi/metric/version',
                           fmt='json')
    return result['version'] + '@' + result['_resolved'].split('#')[1][:7]

@obastatus.command('version {{obastatus.help.version}}')
async def version(msg: Bot.MessageSession):
    await msg.finish(msg.locale.t("obastatus.message.version") + ' ' + await latestVersion())

