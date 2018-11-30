s *.data.yaml | sed -e 's/\(.*\).data.yaml/\1/g' | xargs -n 1 -I {} bash -c "jinja2 --strict --format=yml motionlight.yaml.j2 {}.data.yaml >| ../packages/motionlight_{}.yaml"


