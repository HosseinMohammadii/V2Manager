def check_and_disable_subs(qs):
    disabled_subs = []
    for sub in qs:
        if sub.remained_days < 1:
            sub.disable()
            sub.update_status_dis_time()
            disabled_subs.append(sub)

        elif sub.remained_megabytes < 50:
            sub.disable()
            sub.update_status_dis_traffic()
            disabled_subs.append(sub)

    return disabled_subs


