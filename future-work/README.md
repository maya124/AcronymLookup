# Ideas for Future Work

There is a lot of room to improve this project, so this folder contains some initial progress we made in extending our work. We've also compiled other ideas for how to contribute:
 
### Accuracy
 - characterize the edge cases missed by the constraint satisfaction problem used to pair acronyms with their ground truth definitions
 - retrain model with more acronyms 
 - optimize GloVe feature vector accuracies by increasing the size of vectors or selected context words.
 
 ### Functionality
 - implement calls to existing acronym database (via Stands4 API) for classifying  unseen acronyms
   - potentially using the category of the surrounding text to better hone in on the correct definition
 
 ### User Interface
 - host Chrome extension
 - update Chrome extension to accept user feedback about the validity of the acronym suggestion
 

