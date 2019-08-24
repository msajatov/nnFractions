from Reader import Reader

def main():

    fractions = True
    simple = False
    emb = True
    era = "2017"

    if not fractions:

        samples = "conf/global_config_{0}_{1}.json"

        train_weights = {}
        for channel in ["mt", "et", "tt"]:
            train_weights[channel] = getWeights(samples.format(channel, era), channel, era)

        class_weights = {}
        for cl in ["ztt", "zll", "misc", "tt", "w", "ss", "noniso", "ggh", "qqh"]:
            class_weights[cl] = {}
            for ch in ["mt","et","tt"]:
                tmp = train_weights.get(ch,{})
                class_weights[cl][ch] = tmp.get(cl,0)

        for cl in class_weights:
            print '"{0}":'.format(cl) + " " * (7 - len(cl)), '{' + '"mt":{0}'.format(
                class_weights[cl]["mt"]) + '},'

        for cl in class_weights:
            print '"{0}":'.format(cl) + " " * (7 - len(cl)), '{' + '"et":{0}'.format(
                class_weights[cl]["et"]) + '},'

        for cl in class_weights:
            print '"{0}":'.format(cl) + " " * (7 - len(cl)), '{' + '"tt":{0} '.format(
                class_weights[cl]["tt"]) + '},'
    else:

        if simple:
            samples = "conf/simple_frac_config_{0}_{1}.json"

            train_weights = {}
            for channel in ["mt", "et", "tt"]:
                train_weights[channel] = getWeights(samples.format(channel, era), channel, era)

            class_weights = {}
            for cl in ["tt", "w", "qcd"]:
                class_weights[cl] = {}
                for ch in ["mt", "et", "tt"]:
                    tmp = train_weights.get(ch, {})
                    class_weights[cl][ch] = tmp.get(cl, 0)

            for cl in class_weights:
                print '"{0}":'.format(cl) + " " * (7 - len(cl)), '{' + '"mt":{0}'.format(
                    class_weights[cl]["mt"]) + '},'

            for cl in class_weights:
                print '"{0}":'.format(cl) + " " * (7 - len(cl)), '{' + '"et":{0}'.format(
                    class_weights[cl]["et"]) + '},'

            for cl in class_weights:
                print '"{0}":'.format(cl) + " " * (7 - len(cl)), '{' + '"tt":{0} '.format(
                    class_weights[cl]["tt"]) + '},'
        else:
            if emb:
                samples = "conf/emb_frac_config_{0}_{1}.json"

                train_weights = {}
                for channel in ["mt", "et", "tt"]:
                    train_weights[channel] = getWeights(samples.format(channel, era), channel, era)

                class_weights = {}
                for cl in ["tt", "w", "qcd", "real"]:
                    class_weights[cl] = {}
                    for ch in ["mt", "et", "tt"]:
                        tmp = train_weights.get(ch, {})
                        class_weights[cl][ch] = tmp.get(cl, 0)

                for cl in class_weights:
                    print '"{0}":'.format(cl) + " " * (7 - len(cl)), '{' + '"mt":{0}'.format(
                        class_weights[cl]["mt"]) + '},'

                for cl in class_weights:
                    print '"{0}":'.format(cl) + " " * (7 - len(cl)), '{' + '"et":{0}'.format(
                        class_weights[cl]["et"]) + '},'

                for cl in class_weights:
                    print '"{0}":'.format(cl) + " " * (7 - len(cl)), '{' + '"tt":{0} '.format(
                        class_weights[cl]["tt"]) + '},'

            else:
                samples = "conf/frac_config_{0}_{1}.json"

                train_weights = {}
                for channel in ["mt", "et", "tt"]:
                    train_weights[channel] = getWeights(samples.format(channel, era), channel, era)

                class_weights = {}
                for cl in ["tt", "w", "qcd", "real"]:
                    class_weights[cl] = {}
                    for ch in ["mt", "et", "tt"]:
                        tmp = train_weights.get(ch, {})
                        class_weights[cl][ch] = tmp.get(cl, 0)

                for cl in class_weights:
                    print '"{0}":'.format(cl) + " " * (7 - len(cl)), '{' + '"mt":{0}'.format(
                        class_weights[cl]["mt"]) + '},'

                for cl in class_weights:
                    print '"{0}":'.format(cl) + " " * (7 - len(cl)), '{' + '"et":{0}'.format(
                        class_weights[cl]["et"]) + '},'

                for cl in class_weights:
                    print '"{0}":'.format(cl) + " " * (7 - len(cl)), '{' + '"tt":{0} '.format(
                        class_weights[cl]["tt"]) + '},'


def getWeights(samples, channel, era):

    print "in getWeights"
    train_weights = {}
    read = Reader(channel = channel,
                  config_file = samples,
                  folds=2,
                  era=era)

    numbers = {}
    targets = []
    

    for sample, sampleName in read.get(what = "train"):
        target =  read.config["target_names"][ sample[0]["target"].iloc[0] ]


        numbers[ sampleName["histname"] ] = {"total": len(sample[0]) + len(sample[1]) }
        numbers[ sampleName["histname"] ]["evt"] = sample[0]["event_weight"].sum() + sample[1]["event_weight"].sum()


        if numbers.get(target, None) == None:
            numbers[target] = {"evt": sample[0]["event_weight"].sum() + sample[1]["event_weight"].sum() }
            numbers[target]["total"] = len(sample[0]) + len(sample[1])
            targets.append( target )
        else:
            numbers[target]["evt"] += sample[0]["event_weight"].sum() + sample[1]["event_weight"].sum()
            numbers[target]["total"] += len(sample[0]) + len(sample[1])
        

    total = 0.
    for n in numbers:
        if n in targets: continue
        total += numbers[n]["evt"]
    # print total
    for n in numbers:
        if n not in targets: continue
        train_weights[n] = round(total / numbers[n]["evt"], 1)

        print n+" "*(15 - len(n)) ,round(total / numbers[n]["evt"], 1)

    return train_weights



if __name__ == '__main__':
    main()
