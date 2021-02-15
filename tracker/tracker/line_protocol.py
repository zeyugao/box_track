def parse(data_list):
    res_list = []
    for data in data_list:
        result = data['measurement']

        if data.get("tags"):
            result += ","
            result += ",".join([
                "%s=%s" % (
                    k, v
                ) for k, v in data["tags"].items()
            ])

        result += " "

        result += ",".join([
            "%s=%s" % (
                k, v
            ) for k, v in data["fields"].items()
        ])

        if data.get("time"):
            result += " "
            result += str(data["time"])

        res_list.append(result)
    return '\n'.join(res_list)
