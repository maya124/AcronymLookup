import moxel

model = moxel.Model('maya/acronyms:latest', where='localhost')

output = model.predict(
    sentence = 'NASA is an aeronautical space company'
)

print(output['results'])
