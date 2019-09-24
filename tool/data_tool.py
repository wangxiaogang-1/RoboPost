


def queryset_transducer(queryset):
    result_list = []
    for item in queryset:
        if isinstance(item, tuple):
            items = []
            for tup in item:
                items.append(tup)
        elif isinstance(item, dict):
            items = {}
            for key in item:
                items[key] = item[key]
        result_list.append(items)
    return result_list
