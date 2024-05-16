import numpy as np

eps = 1e-5


def calc_confusion_matrix(y_true, y_pred):
    mask = y_true == 1
    tp = np.sum(y_pred[mask] == 1)
    fn = np.sum(mask) - tp

    fp = np.sum(y_pred[np.logical_not(mask)] == 1)
    tn = np.sum(np.logical_not(mask)) - fp

    return np.array([[tp, fn], [fp, tn]])


def perf_metrics(y_actual, y_hat, threshold):
    mask = y_hat >= threshold
    y_predict = np.zeros(shape=y_actual.shape)
    y_predict[mask] = 1

    conf_matrix = calc_confusion_matrix(y_actual, y_predict)

    tp = conf_matrix[0][0]
    fn = conf_matrix[0][1]
    fp = conf_matrix[1][0]
    tn = conf_matrix[1][1]

    tpr = tp / (tp + fn + eps)
    fpr = fp / (tn + fp + eps)

    return fpr, tpr


class Metric:
    def __init__(self):
        """init"""

    def calc_metric(self, y_true: np.ndarray, y_pred: np.ndarray):
        """loss calculation"""


class RMSE(Metric):
    def calc_metric(self, y_true: np.ndarray, y_pred: np.ndarray):
        err = y_true - y_pred
        return np.sqrt(np.sum(err * err)) / len(err)


class F1Score(Metric):

    def calc_metric(self, y_true: np.ndarray, y_pred: np.ndarray):
        unique, counts = np.unique(y_true, return_counts=True)
        if (unique.size == 2):
            conf_matrix = calc_confusion_matrix(y_true, y_pred)
        else:
            confs = np.zeros((unique.size, 2, 2))
            for i in range(unique.size):
                y_true_this_label = np.zeros(y_true.shape)
                y_true_this_label[y_true == unique[i]] = 1

                y_pred_this_label = np.zeros(y_pred.shape)
                y_pred_this_label[y_pred == unique[i]] = 1

                confs[i] = calc_confusion_matrix(y_true_this_label, y_pred_this_label).copy()

            conf_matrix = np.average(confs, axis=0)

        res = 2 * conf_matrix[0][0] / (2 * conf_matrix[0][0] + conf_matrix[1][0] + conf_matrix[0][1])
        return res


class RocAuc(Metric):

    def calc_metric(self, y_true: np.ndarray, y_prob: np.ndarray):
        unique = np.unique(y_true)
        thresholds = np.sort(np.unique(y_prob))

        points_tpr = None
        points_fpr = None

        if (unique.size == 2):
            points_tpr = np.zeros(thresholds.shape)
            points_fpr = np.zeros(thresholds.shape)
            n = int(thresholds.size)
            for j in range(n - 1, -1, -1):
                fpr, tpr = perf_metrics(y_true, y_prob, thresholds[j])
                points_fpr[j] = fpr
                points_tpr[j] = tpr
            auc = np.sum(np.trapz(points_tpr, points_fpr))
        else:
            auc_per_label = np.zeros(shape=(unique.size,))
            points_tpr = np.zeros((unique.size, thresholds.size))
            points_fpr = np.zeros((unique.size, thresholds.size))
            for i in range(unique.size):
                n = int(thresholds.size)
                for j in range(n - 1, -1, -1):
                    y_true_this_label = np.zeros(y_true.shape)
                    y_true_this_label[y_true == unique[i]] = 1

                    fpr, tpr = perf_metrics(y_true_this_label, y_prob[:, i], thresholds[j])
                    points_fpr[i][j] = fpr
                    points_tpr[i][j] = tpr

                auc_per_label[i] = -np.sum(np.trapz(np.array(points_tpr[i]), np.array(points_fpr[i])))
            auc = auc_per_label

        return auc, points_tpr, points_fpr


class Acuracy(Metric):

    def calc_metric(self, y_true: np.ndarray, y_pred: np.ndarray):
        is_true = np.zeros(y_true.shape)
        is_true[y_true == y_pred] = 1

        return np.sum(is_true) / y_true.size