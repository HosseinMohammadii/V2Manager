def check_and_disable_subs(qs):
    disabled_subs = []
    for sub in qs:
        if sub.remained_days < 0:
            sub.disable()
            sub.update_status_dis_time()
            disabled_subs.append(sub)
            a = sub.realtime_remained_megabytes

        elif sub.realtime_remained_megabytes < 0:
            sub.disable()
            sub.update_status_dis_traffic()
            disabled_subs.append(sub)

    return disabled_subs


def update_traffic(qs):
    disabled_subs = []
    for sub in qs:
        a = sub.realtime_remained_megabytes
        disabled_subs.append(sub)

    return disabled_subs


