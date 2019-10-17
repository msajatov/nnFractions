import root_pandas as rp
import root_numpy as rn
import utils.Plotting as pl
from Tools.VarObject.VarObject import Var
from Tools.Weights.Weights import Weight
from pandas import DataFrame, concat


def main():


    prediction = DataFrame([[1, 20, 3, 4,], [2, 3, 40, 5], [30, 4, 5, 6], [4, 5, 66, 7]])

    print prediction

    headers = []



    print prediction

    prediction = prediction.astype(float)

    print prediction

    # note: idxmax uses the header string -> if this string contains something other than numbers, it cannot be parsed
    # to float and will remain a string
    df = DataFrame(dtype = float, data = { "predicted_class":prediction.idxmax(axis=1).values,
                            "predicted_prob": prediction.max(axis=1).values } )

    print df

    # renaming of column headers must happen AFTER selecting predicted_class
    for i in range (0,len(prediction.columns)):
        headers.append("predicted_prob_" + str(i))

    prediction.columns = headers

    print prediction

    result = concat([prediction, df], axis=1)

    print result


    # #df = DataFrame(dtype = float, data = { "predicted_class":prediction.idxmax(axis=1).values,
    # #                         "predicted_prob": prediction.max(axis=1).values } )
    #
    # predicted_class_df = DataFrame(dtype=float, data={"predicted_class": prob_df.idxmax(axis=1).values})
    # #predicted_class_df = predicted_class_df.replace("predicted_prob_", "", regex=True)
    # #predicted_class_df = predicted_class_df.astype(float)
    #
    # predicted_prob_df = DataFrame(dtype=float, data={"predicted_prob": prob_df.max(axis=1).values})
    #
    # prediction['predicted_class'] = predicted_class_df["predicted_class"].values.astype(float)
    # prediction['predicted_prob'] = predicted_prob_df["predicted_prob"].values.astype(float)
    #
    # #result = concat([prediction, df], axis=1)
    # #prediction["predicted_class"] = df["predicted_class"].values
    # #prediction["predicted_prob"] = df["predicted_prob"].values


if __name__ == '__main__':
    main()