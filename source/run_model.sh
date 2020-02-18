CH=$1
ERA=$2
NAME=$3
VARSET=$4

runner.sh "python run_model.py -c ${CH} -e ${ERA} -t -p -f -s standard -name ${NAME} -varset ${VARSET}"

mv nohup.out nohup_${NAME}_${VARSET}_${CH}_${ERA}.out

python moveNohup.py -c ${CH} -e ${ERA} -name ${NAME} -varset ${VARSET} &