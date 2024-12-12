# What is an instance collection ?
It's an object which refers to a collection content linked from another file, or from your main file.
This way, you can get multiple copies of linked data very easily.

# Why it's usefull ?
Because Instance collections is one of the best feature of blender, allowing to instanciate a group of objects, whatever their type are.

# What is Instance Collection toolbox for ? 
This toolbox contains some helpful tools when you are using instance collection. The tools are : 

![Tab](https://github.com/user-attachments/assets/a3bfc691-3301-4a91-929b-2e1872b633da)

## Sel to Inst :  convert selected objects into a new instance collection. Few options are available :
  - New Collection Name : Choose your name of your Instance Collection. By default, "Random ID" will create a name with 5 random letters
  - Use Collection Label (checked by default) : Will use the prefix set in the preferences (section later)
  - Collection Color (random by default) : Will change the color of the collection. If you want a defined color, change it
  - Keep Original Location (checked by default) : Will make the instance collection be at the same location which means nothing moves. If unchecked, the instance collection will be moved to the center of the world
  - Collection Center : Every Instance collection has a kind of origin. You can choose either World Origin, 2D Cursor, Collection Center, Collection center with Z on 0
  - Store in Asset Browser : it will automatically store the instance collection as an asset. The Asset Manager has to be opened to make it work 

![Sel to inst options](https://github.com/user-attachments/assets/eb61fd5e-965a-44f6-bdbb-840180dc4daa)

## Coll to Inst : convert selected collection into a new instance collection. Few options are available :
 - Use Collection Label (checked by default) : Will use the prefix set in the preferences (section later)
 - Collection Color (Current by default) : Will set the color of the collection. If you want a defined color, change it, but by default it will use the one set in the selected collection
 - Keep Original Location (checked by default) : Will make the instance collection be at the same location which means nothing moves. If unchecked, the instance collection will be moved to the center of the world
 - Collection Center : Every Instance collection has a kind of origin. You can choose either World Origin, 2D Cursor, Collection Center, Collection center with Z on 0
 - Store in Asset Browser : it will automatically store the instance collection as an asset. The Asset Manager has to be opened to make it work

![Coll to inst options](https://github.com/user-attachments/assets/916ecde5-af1f-4f7e-95fa-64608ceddd72)

## Inst to Coll : The revert action of Coll to Inst :
  It will re-link the original collection in the current scene

## Update Asset Manager :  
  It will update the Asset Manager with all the collection in the current scene

## Rename Data : Allow you to synchronize the data and the object. Two options are available :
  - Data renames Object : the name of the data will rename all the selected objects
  - Object renames Data : the name of the object will rename all the selected data

# Addon Preferences :
![Prefs](https://github.com/user-attachments/assets/5a45e29a-42aa-4866-a523-dda9120c9826)

Few Preferences are available for the user :
  - Label: By default "ROOT_", it will put this label as a prefix or a suffix, to unify the naming convention of your elements
  - Scene Library (checked by default) : all the collections will be stored in a unique file (name "InstanceCollections_Library" by default), to allow you to change your collections
  - Store in Asset Browser (checked by default) : will store instance collection created by default in the Asset Browser





