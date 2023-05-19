from utils.uri import get_original_confs_from_subscription, get_edited_confs


def get_edited_confs_func(subs):
    from subscribe.models import Subscription
    sub: Subscription
    from subscribe.models import PanelTypes, LinkTypes
    all = []
    for l in subs.link_set.all():
        if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.BY_CONFIG_ID:

            original_confs = l.get_marzban_confs_by_config_id()

            if len(original_confs) == 0:
                continue

            edited_confs = get_edited_confs(original_confs, l.server.get_mss())
            all += edited_confs

        if l.server.panel == PanelTypes.MARZBAN and l.type == LinkTypes.URI_LIST:

            original_confs = list(filter(lambda x: len(x) > 0, l.value.split("\n")))

            if len(original_confs) == 0:
                continue

            edited_confs = get_edited_confs(original_confs, l.server.get_mss())
            all += edited_confs

        if l.server.panel == PanelTypes.XUI and l.type == LinkTypes.URI:
            edited_confs = get_edited_confs([l.value], l.server.get_mss())
            all += edited_confs

    return all
