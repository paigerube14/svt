app_array=("django")

file_name="conc_builds_2.out"

for proj in "${app_array[@]}"
do
  echo "================ Average times for $proj app =================" >> $file_name
  proj_file_name="conc_builds_$proj.out"
  grep "Average build time, all good builds" $proj_file_name >> $file_name
  grep "Average push time, all good builds" $proj_file_name >> $file_name
  grep "Good builds included in stats" $proj_file_name >> $file_name
  echo "==============================================================" >> $file_name
done

cat $file_name