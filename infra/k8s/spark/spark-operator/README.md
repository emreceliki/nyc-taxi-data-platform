
## Add Spark operator helm repo
```bash
helm repo add \
spark-operator \
https://kubeflow.github.io/spark-operator

helm repo update
```

## Create namespace for spark operator
```bash
kubectl create ns spark-operator
```

## Install with helm
```bash
helm install \
my-spark-operator \
spark-operator/spark-operator \
--namespace spark-operator \
--set webhook.enable=true
```

## Check resources
```bash
kubectl get all -n spark-operator


NAME                                                READY   STATUS    RESTARTS   AGE
pod/my-spark-operator-controller-68658b59c7-8g6sx   1/1     Running   0          18s
pod/my-spark-operator-webhook-786d69bbd5-6jbd4      1/1     Running   0          18s

NAME                                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
service/my-spark-operator-webhook-svc   ClusterIP   10.101.151.51   <none>        9443/TCP   18s

NAME                                           READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/my-spark-operator-controller   1/1     1            1           18s
deployment.apps/my-spark-operator-webhook      1/1     1            1           18s

NAME                                                      DESIRED   CURRENT   READY   AGE
replicaset.apps/my-spark-operator-controller-68658b59c7   1         1         1       18s
replicaset.apps/my-spark-operator-webhook-786d69bbd5      1         1         1       18s
```

## Create service account
```bash
kubectl create serviceaccount spark

kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default
```
