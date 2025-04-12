bl_info = {
    "name": "Instance Collections Toolbox",
    "author": "Yannick 'BoUBoU' Castaing",
    "description": "This addon is a toolset which make you manage easily collections as libraries",
    "location": "View3D > UI > Workflow",
    "doc_url": "",
    "warning": "",
    "category": "Workflow",
    "blender": (2,91,0),
    "version": (1,5,4)
}

# get addon name and version to use them automaticaly in the addon
Addon_Name = str(bl_info["name"])
Addon_Version = str(bl_info["version"]).replace(",",".").replace("(","").replace(")","")

### import modules ###
import bpy
from statistics import mean
from random import choice
from random import randrange
from string import ascii_uppercase
from time import sleep

### define global variables ###
debug_mode = True
separator = "-" * 20

blender_version = f"{bpy.app.version[0]}.{bpy.app.version[1]}"

tool_a = "Rename selection from its data"
tool_b = "Set collections center from selection"
tool_c = "Convert Mesh to Instance Collection"
tool_f = "Selection to Instance Collection"
tool_h = "Collection to Instance Collection"
tool_i = "Instance Collection to Collection Selection"

default_sceneLib_name = "InstanceCollections_Library"

default_coll_name = f'"Random ID"'

coll_color_options = [
                        ("RANDOM", "Random", "", 0),
                        ("CURRENT", "Current", "", 1),
                        ("NONE", "", "","OUTLINER_COLLECTION", 2),
                        ("COLOR_01", "", "", "COLLECTION_COLOR_01",3),
                        ("COLOR_02", "", "", "COLLECTION_COLOR_02",4),
                        ("COLOR_03", "", "", "COLLECTION_COLOR_03",5),
                        ("COLOR_04", "", "", "COLLECTION_COLOR_04", 6),
                        ("COLOR_05", "", "", "COLLECTION_COLOR_05", 7),
                        ("COLOR_06", "", "", "COLLECTION_COLOR_06", 8),
                        ("COLOR_07", "", "", "COLLECTION_COLOR_07", 9),
                        ("COLOR_08", "", "", "COLLECTION_COLOR_08", 10),
                        ]
coll_center_options = [
                ("World", "World Origin", "collection center at (0,0,0)",0),
                ("2D Cursor","2D Cursor","position of the 2D cursor",1),
                ("Collection Center", "Collection Center", "collection center at center of selected objects",2),
                ("Coll_except_Z", "Collection Center with Z on the floor", "collection center at center of selected objects, but z = 0",3),
                ]

## define addon preferences
class INSTCOLL_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    user_label_pref : bpy.props.StringProperty(name="Label", default="ROOT_", description="default label for automatic collections")
    user_labelPos_pref: bpy.props.EnumProperty(name = "Label Position",description = "choose selection type",items = [("Prefix","Prefix","Prefix",0),("Suffix","Suffix","Suffix",1)],default=0)
    user_sceneLib_checkbox_pref : bpy.props.BoolProperty (name="",description="Store original instance collections into a scene",default=True) 
    user_sceneLib_pref : bpy.props.StringProperty(name="Scene Library", default=default_sceneLib_name, description="default scene for automatic library")
    storeInAssetBrowser_pref : bpy.props.BoolProperty(name="Store in Asset Browser", default=True, description="store into the asset browser")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        split = row.split(factor=2/3)
        split.prop(self, "user_label_pref")
        split.prop(self, "user_labelPos_pref")
        row = layout.row()
        split = row.split(factor=.05)
        split.prop(self, "user_sceneLib_checkbox_pref")
        split.prop(self, "user_sceneLib_pref")
        row.prop(self, "storeInAssetBrowser_pref")

### create property ###
class INSTCOLL_properties (bpy.types.PropertyGroup):
    # insColl_scene_library_checkbox_prop : bpy.props.BoolProperty (name="Scene Library",description="Store original instance collections into a scene",default=True) 
    insColl_scene_library_prop : bpy.props.PointerProperty (type=bpy.types.Scene, name="Save in", description=f'Wanted scene library. If empty, the scene will be created and filled by default, named "{default_sceneLib_name}"')
    coll_color_prop : bpy.props.EnumProperty(items = coll_color_options, name = "Collection color", description = "Give the created collection a random color", default = 0)
    coll_original_location_prop: bpy.props.BoolProperty(name = 'Keep original location',description = "Keep the original location of selected elements",default = True)

    rename_dataToObject_option = [("Data blocks > Objects","Data rename Object","Data blocks rename objects. The main behavior",1),
                        ("Objects > Data blocks","Object rename Data","Objects rename Data. WARNING : may cause strange behavior if instanced data !!",2),        
                        ]   
    rename_dataToObject_prop : bpy.props.EnumProperty(items = rename_dataToObject_option, name = "Rename behavior", description = "conforms names between datas and objects", default=1,)

### create panels ###
# create panel UPPER_PT_lower
class VIEW3D_PT_instcoltoolbox_all(bpy.types.Panel):
    bl_label = f"{Addon_Name} - {Addon_Version}"
    bl_idname = "VIEW3D_PT_instcoltoolbox_all"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Workflow" 

    def draw_header(self, context):
        self.layout.label(text="", icon='OUTLINER_OB_GROUP_INSTANCE')  
     
    def draw(self, context):
        instanceColl_props = context.scene.instanceColl_props

        layout = self.layout
        # convert to instance collection
        #layout.label(text="Convert into Instance Collections")
        #rowFull = layout.row()
        #split = rowFull.split(factor=.5)
        box = layout.box()
        row = box.row()
        #subsplit = row.split(factor=.5)
        #subsplit.operator("object.instcol_seltoinstancecollection",text="",icon="RESTRICT_SELECT_OFF")
        #subsplit.operator("object.instcol_colltoinstancecollection",text="",icon="OUTLINER_COLLECTION")
        row.operator("object.instcol_seltoinstancecollection",text="Sel to Inst",icon="RESTRICT_SELECT_OFF")
        row.operator("object.instcol_colltoinstancecollection",text="Coll to Inst",icon="OUTLINER_COLLECTION")
        row = box.row()
        row.operator("object.instcol_instancecollectiontosel",text="Inst to Coll",icon="RECOVER_LAST")
        row.operator("object.instcol_updateassetbrowser",text="Update AM",icon="ASSET_MANAGER")
        row = box.row()
        row.operator("object.instcol_renameselection",text = "Rename Data",icon="SORTALPHA")
        row.label(text="")
        # subsplit = row.split(factor=.5)
        # subsplit.operator("object.instcol_instancecollectiontosel",text="",icon="RECOVER_LAST")
        # subsplit.operator("object.instcol_updateassetbrowser",text="",icon="ASSET_MANAGER")
        # row = box.row()
        # subsplit = row.split(factor=.5)
        # subsplit.operator("object.instcol_renameselection",text = "",icon="SORTALPHA")
        # subsplit.label(text="")
        # box = layout.box()
        # row = box.row()
        # subsplit = row.split(factor=.5)
        # subsplit.operator("object.instcol_collectioncenter",text = "",icon="LIBRARY_DATA_OVERRIDE")
        # subsplit.operator("object.instcol_renameselection",text = "",icon="SORTALPHA")
        # row = box.row()
        # subsplit = row.split(factor=.5)
        # # subsplit.operator("object.instcol_meshtocollection",text="",icon="EXPERIMENTAL")
        # subsplit.label(text="")
        # subsplit.label(text="")
        

# class VIEW3D_PT_instcoladdtools(bpy.types.Panel):
#     bl_label = f"Additional Tools"
#     bl_idname = "VIEW3D_PT_instcoladdtools"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "Workflow"  
#     bl_parent_id = "VIEW3D_PT_instcoltoolbox_all"
#     bl_options = {"DEFAULT_CLOSED"}

#     def draw(self, context):
#         instanceColl_props = context.scene.instanceColl_props

#         layout = self.layout
#         ## tools
#         layout.label(text="Additional tools")
#         box = layout.box()
#         row = box.row()
#         row.operator("object.instcol_collectioncenter",text = tool_b,icon="LIBRARY_DATA_OVERRIDE")
#         row.operator("object.instcol_renameselection",text = tool_a,icon="SORTALPHA")
#         row = box.row()
#         row.operator("object.instcol_meshtocollection",text=tool_c,icon="EXPERIMENTAL")
#         row.label(text="")


### create functions ###
# omc : object, meshes, collection lists
def omc_lists():
    objects_list = []
    meshes_list = []
    coll_list = []
    if len(bpy.context.selected_objects) > 0:
        for obj in bpy.context.selected_objects:
            objects_list.append(obj)
            if obj.type == 'MESH':
                meshes_list.append(obj)
            elif obj.type == 'EMPTY' and obj.instance_type == 'COLLECTION':
                coll_list.append(obj)

# create scene library
def create_libraryScene_func(new_coll_name = ""):
    if bpy.context.preferences.addons[__name__].preferences.user_sceneLib_pref:
        working_scene = bpy.context.scene
        default_sceneLib_name = bpy.context.preferences.addons[__name__].preferences.user_sceneLib_pref
        user_library_scene = bpy.context.scene.instanceColl_props.insColl_scene_library_prop
        # create lib scene by default
        if user_library_scene == None:
            if default_sceneLib_name not in bpy.data.scenes.keys():
                bpy.ops.scene.new(type='NEW')
                bpy.context.scene.name = default_sceneLib_name
            bpy.context.scene.instanceColl_props.insColl_scene_library_prop = bpy.data.scenes[default_sceneLib_name]
        bpy.context.window.scene = bpy.context.scene.instanceColl_props.insColl_scene_library_prop
        # link new collection scene
        bpy.context.scene.collection.children.link(bpy.data.collections[new_coll_name])
        # get back to original work scene
        bpy.context.window.scene = working_scene    

#make sure new collection name is unique
def increment_name_func(new_coll_name,mid_name=""):
    complete_name = f"{new_coll_name}{mid_name}"
    if complete_name in bpy.data.collections.keys():   
        iter = 1
        iter_inc = str(iter).zfill(3)
        while f"{complete_name}.{iter_inc}" in bpy.data.collections.keys():
            iter += 1
            iter_inc = str(iter).zfill(3)
        new_coll_name = f"{complete_name}.{iter_inc}"
    else:
        new_coll_name = complete_name
    return new_coll_name

# create coll unique id
def new_coll_id_func():
    # random name for collection
    new_coll_id = []
    for i in range(0,5):
        i = choice(ascii_uppercase)
        new_coll_id.append(i)
    new_coll_id = "".join(new_coll_id)
    return new_coll_id

# rename objects from their data block
def rename_from_datablock_func(selection,solo):
    if solo == True:
        if selection.name in bpy.data.objects.keys(): #trick for sel to instance coll
            if selection.type == 'MESH':
                bpy.data.objects[selection.name].name = bpy.data.objects[selection.name].data.name
            elif selection.type == 'EMPTY' and selection.instance_type == 'COLLECTION':
                if selection.instance_collection != None:
                    bpy.data.objects[selection.name].name = bpy.data.objects[selection.name].instance_collection.name
    elif len(selection)>0:
        for obj in selection:
            if obj.type == 'MESH':
                bpy.data.objects[obj.name].name = bpy.data.objects[obj.name].data.name
            elif obj.type == 'EMPTY' and obj.instance_type == 'COLLECTION':
                if obj.instance_collection != None:
                    bpy.data.objects[obj.name].name = bpy.data.objects[obj.name].instance_collection.name

# bank into the asset browser
def storeIn_AssetBrowser_func(selected_coll,blender_version):
    if bpy.data.filepath != '':
        bpy.data.collections[selected_coll].asset_mark()
        # Spécifier un chemin de fichier pour sauvegarder l'asset (mettre à jour le chemin si nécessaire)
        blend_file_path = bpy.data.filepath
        # # Sauvegarder le fichier contenant l'asset
        # bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)
        # Changer le contexte de l'Asset Browser pour utiliser la bibliothèque locale
        for area in bpy.context.screen.areas:
            if area.type == 'FILE_BROWSER':
                space_data = area.spaces.active
                # Changer la référence de la bibliothèque d'assets à 'LOCAL'
                if int(blender_version[0])<4:
                    print("version inf 4")
                    space_data.params.asset_library_ref = 'LOCAL'
                    space_data.params.import_type = 'LINK'
                elif int(blender_version[0])>=4:
                    print("version 4+")
                    space_data.params.asset_library_reference = 'LOCAL'
                    space_data.params.import_method = 'LINK'
                # Générer la prévisualisation pour l'asset
                bpy.ops.ed.lib_id_generate_preview({'id': bpy.data.collections[selected_coll]})
                sleep(.1) # a bit of time otherwise preview problems
                #break


### create operators ###
# create operator UPPER_OT_lower and idname = upper.lower       
class OBJECT_OT_instcoll_seltoinstancecollection(bpy.types.Operator):
    bl_idname = 'object.instcol_seltoinstancecollection'
    bl_label = "Convert selection to instance collection"
    bl_description = "Selected elements will be transform in a instance selection, and will be libraryed in a library scene"
    bl_options = {"REGISTER", "UNDO"}
               
    # redo panel = user interraction
    instcol_newColName: bpy.props.StringProperty(name = "New Collection Name", description = "Give the new collection a name", default = default_coll_name)

    use_prefLabel_prop: bpy.props.BoolProperty(name = 'Use Collection Label',description = "use the label from addon preferences",default = True)
    coll_color_prop : bpy.props.EnumProperty(items = coll_color_options, name = "Collection color", description = "Give the created collection a random color", default = 0,)
    coll_original_location_prop: bpy.props.BoolProperty(name = 'Keep original location',description = "Keep the original location of selected elements",default = True)
    coll_center_prop : bpy.props.EnumProperty(items = coll_center_options,name = "Collection center",description = "collection center",default=2,)
    storeAsset_prop: bpy.props.BoolProperty(name = 'Store in Asset Browser',description = "if checked, store in asset browser",default = True)
    
    def execute(self, context):
        print(f"\n {separator} Begin {Addon_Name} - {tool_f} {separator} \n")
        
        coll_center_prop = self.coll_center_prop
        coll_original_location_prop = self.coll_original_location_prop
        storeAsset_prop = self.storeAsset_prop
        
        #get preferences
        user_label_pref = bpy.context.preferences.addons[__name__].preferences.user_label_pref
        user_labelPos_pref = bpy.context.preferences.addons[__name__].preferences.user_labelPos_pref
        #user_sceneLib_pref = bpy.context.preferences.addons[__name__].preferences.user_sceneLib_pref
        storeInAssetBrowser_pref = bpy.context.preferences.addons[__name__].preferences.storeInAssetBrowser_pref

        if len(bpy.context.selected_objects)>0:
            sel_loc_x = []
            sel_loc_y = []
            sel_loc_z = []
            med_sel_x = 0
            med_sel_y = 0
            med_sel_z = 0
            coord_z = med_sel_z
            
            # random name for collection
            new_coll_id = new_coll_id_func()
            
            # save selection set
            selected_obj = []
            for obj in bpy.context.selected_objects:
                selected_obj.append(obj)
                
            # set scene collection as active collection
            scene_collection = bpy.context.view_layer.layer_collection
            bpy.context.view_layer.active_layer_collection = scene_collection
            
            # generate collection id
            if self.instcol_newColName == default_coll_name: # user choice
                new_coll_name = new_coll_id
            elif self.instcol_newColName in bpy.data.collections.keys(): # user choice but already existing
                new_coll_name = increment_name_func(self.instcol_newColName)
            else: # default choice
                new_coll_name = self.instcol_newColName

             # Update default coll nam regarding user pref
            if self.use_prefLabel_prop:
                if user_labelPos_pref == "Prefix":
                    new_coll_name = f"{user_label_pref}{new_coll_name}"
                else : 
                    new_coll_name = f"{new_coll_name}{user_label_pref}"

            # unlink selected objects from their collection, and put them in scene collection
            for obj in selected_obj:
                if obj in bpy.context.scene.collection.objects.values():
                    bpy.context.scene.collection.objects.unlink(bpy.data.objects[obj.name])
            for obj in bpy.context.selected_objects:
                for col in bpy.context.scene.objects[obj.name].users_collection:
                    bpy.data.collections[col.name].objects.unlink(bpy.data.objects[obj.name])

            # create new collection
            bpy.ops.collection.create(name = new_coll_name)
            bpy.context.scene.collection.children.link(bpy.data.collections[new_coll_name])
            for obj in selected_obj:
                bpy.data.collections[new_coll_name].objects.link(bpy.data.objects[obj.name])

            # create selection offset from each collection
            if len(selected_obj)>0:
                if coll_center_prop == "Coll_except_Z" or coll_center_prop == "Collection Center": 
                
                    for obj in selected_obj:
                        sel_loc_x.append(obj.location.x)
                        sel_loc_y.append(obj.location.y)
                        sel_loc_z.append(obj.location.z)
                    med_sel_x = mean(sel_loc_x)
                    med_sel_y = mean(sel_loc_y)
                    med_sel_z = mean(sel_loc_z)
                    if coll_center_prop == "Coll_except_Z":
                        coord_z = 0
                    if coll_center_prop == "Collection Center":
                        coord_z = med_sel_z
                elif coll_center_prop == "2D Cursor":
                    med_sel_x =  bpy.context.scene.cursor.location[0]
                    med_sel_y = bpy.context.scene.cursor.location[1]
                    coord_z = bpy.context.scene.cursor.location[2]
                elif coll_center_prop == "World":
                    med_sel_x = 0
                    med_sel_y = 0
                    coord_z = 0
                    bpy.data.collections[new_coll_name].instance_offset = (0,0,0)
                bpy.data.collections[new_coll_name].instance_offset = (med_sel_x,med_sel_y,coord_z)
                
            # unlink new collection from scene
            bpy.context.scene.collection.children.unlink(bpy.data.collections[new_coll_name])
          
            # create instance collection
            bpy.ops.object.add()
            new_coll_root = bpy.context.active_object
            rename_from_datablock_func(new_coll_root,True)
            new_coll_root.name = new_coll_name
            if coll_original_location_prop==True:
                new_coll_root.location = (med_sel_x,med_sel_y,coord_z)
            bpy.data.objects[new_coll_root.name].instance_type = 'COLLECTION'
            new_coll_root.instance_collection = bpy.data.collections[new_coll_name]
            if self.coll_color_prop == "RANDOM" or self.coll_color_prop == "CURRENT":
                color_id = randrange(1,9)
                bpy.data.collections[new_coll_root.name].color_tag = f"COLOR_0{color_id}"
            else:
                bpy.data.collections[new_coll_root.name].color_tag = self.coll_color_prop

            # create scene library and link new collection in it
            create_libraryScene_func(new_coll_name)

            # store in asset browser
            if storeAsset_prop:
                storeIn_AssetBrowser_func(new_coll_name,blender_version)

            # reset the collection name
            self.instcol_newColName = default_coll_name        

            # show informations
            print("selected_obj : " + str(selected_obj))
            print("new_coll_name : " + str(new_coll_name))

        print(f"\n {separator} {Addon_Name} - {tool_f} Finished {separator} \n")
        
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

# create operator UPPER_OT_lower and idname = upper.lower
class OBJECT_OT_instcoll_colltoinstancecollection(bpy.types.Operator):
    bl_idname = 'object.instcol_colltoinstancecollection'
    bl_label = "Collection to Instance collection"
    bl_description = "Convert active collection to an instance collection"
    bl_options = {"REGISTER", "UNDO"}

    # # redo panel = user interraction
    use_prefLabel_prop: bpy.props.BoolProperty(name = 'Use Collection Label',description = "use the label from addon preferences",default = True)
    coll_color_prop : bpy.props.EnumProperty(items = coll_color_options,name = "Collection color",description = "Give the created collection a random color",default = 1,)
    coll_center_prop : bpy.props.EnumProperty(items = coll_center_options,name = "Collection center",description = "collection center",default=2,)
    coll_original_location: bpy.props.BoolProperty(name = 'Keep original location',description = "Keep the original location of selected elements",default = True)
    storeAsset_prop: bpy.props.BoolProperty(name = 'Store in Asset Browser',description = "if checked, store in asset browser",default = True)
    #instcol_storeintotherandomlibrary: bpy.props.BoolProperty(name = 'Store copy into "Randomize Library"',description = "Store the newly created collection into the randomize library",default = False)
    #suffix_randomizelibrary : bpy.props.StringProperty(name = "RandomizeLibrary_",description = "add a suffix to the library collection",default="ALL",    ) 
    #coll_center_prop : bpy.props.EnumProperty(items = coll_center_options,name = "Collection center",description = "collection center",default=2,)
    
    def execute(self, context):
        print(f"\n {separator} Begin {Addon_Name} - {tool_f} {separator} \n")

        user_label_pref = bpy.context.preferences.addons[__name__].preferences.user_label_pref
        user_labelPos_pref = bpy.context.preferences.addons[__name__].preferences.user_labelPos_pref
        #user_sceneLib_pref = bpy.context.preferences.addons[__name__].preferences.user_sceneLib_pref
        storeInAssetBrowser_pref = bpy.context.preferences.addons[__name__].preferences.storeInAssetBrowser_pref

        coll_center_prop = self.coll_center_prop
        storeAsset_prop = self.storeAsset_prop
        
        # get active collection
        active_coll = bpy.context.view_layer.active_layer_collection
        active_coll_color = bpy.data.collections[bpy.context.view_layer.active_layer_collection.name].color_tag

        sel_loc_x = []
        sel_loc_y = []
        sel_loc_z = []
        med_sel_x = 0
        med_sel_y = 0
        med_sel_z = 0
        coord_z = med_sel_z
        
        # random name for collection
        new_coll_id = []
        for i in range(0,5):
            i = choice(ascii_uppercase)
            new_coll_id.append(i)
        new_coll_id = "".join(new_coll_id)
        
        # save selection set
        selected_obj = bpy.data.collections[bpy.context.view_layer.active_layer_collection.name].objects
        new_coll_name = bpy.context.view_layer.active_layer_collection.name
        
        print(selected_obj.keys())

        # set scene collection as active collection
        scene_collection = bpy.context.view_layer.layer_collection
        bpy.context.view_layer.active_layer_collection = scene_collection

        print(selected_obj.keys())

        # unlink selected objects from their collection, and put them in scene collection
        stored_obj = []
        if len(selected_obj)>0 and new_coll_name != "Master Collection":
            for obj in selected_obj:
                for coll in bpy.context.scene.objects[obj.name].users_collection:
                    bpy.data.collections[coll.name].objects.unlink(bpy.data.objects[obj.name])
                #bpy.context.scene.collection.objects.link(bpy.data.objects[obj.name])
                stored_obj.append(obj)
            bpy.data.collections.remove(bpy.data.collections[coll.name])
        else:
            bpy.data.collections.remove(bpy.data.collections[active_coll.name])

        # Update default coll nam regarding user pref
        if self.use_prefLabel_prop:
            if user_labelPos_pref == "Prefix":
                new_coll_name = f"{user_label_pref}{new_coll_name}"
            else : 
                new_coll_name = f"{new_coll_name}{user_label_pref}"

        # create new collection
        bpy.ops.collection.create(name = new_coll_name)
        bpy.context.scene.collection.children.link(bpy.data.collections[new_coll_name])
        for obj in stored_obj:
            bpy.data.collections[new_coll_name].objects.link(bpy.data.objects[obj.name])

        # create selection offset from each collection
        if len(selected_obj)>0:
                if coll_center_prop == "Coll_except_Z" or coll_center_prop == "Collection Center": 
                
                    for obj in selected_obj:
                        sel_loc_x.append(obj.location.x)
                        sel_loc_y.append(obj.location.y)
                        sel_loc_z.append(obj.location.z)
                    med_sel_x = mean(sel_loc_x)
                    med_sel_y = mean(sel_loc_y)
                    med_sel_z = mean(sel_loc_z)
                    if coll_center_prop == "Coll_except_Z":
                        coord_z = 0
                    if coll_center_prop == "Collection Center":
                        coord_z = med_sel_z
                elif coll_center_prop == "2D Cursor":
                    med_sel_x =  bpy.context.scene.cursor.location[0]
                    med_sel_y = bpy.context.scene.cursor.location[1]
                    coord_z = bpy.context.scene.cursor.location[2]
                elif coll_center_prop == "World":
                    med_sel_x = 0
                    med_sel_y = 0
                    coord_z = 0
                    bpy.data.collections[new_coll_name].instance_offset = (0,0,0)
                bpy.data.collections[new_coll_name].instance_offset = (med_sel_x,med_sel_y,coord_z)

        # unlink new collection from scene
        bpy.context.scene.collection.children.unlink(bpy.data.collections[new_coll_name])
        
        # create instance collection
        bpy.ops.object.add()
        new_coll_root = bpy.context.active_object
        new_coll_root.name = new_coll_name
        if self.coll_original_location==True:
            new_coll_root.location = (med_sel_x,med_sel_y,0)
        bpy.data.objects[new_coll_root.name].instance_type = 'COLLECTION'
        new_coll_root.instance_collection = bpy.data.collections[new_coll_name]
        if self.coll_color_prop == "RANDOM":
            color_id = randrange(1,9)
            bpy.data.collections[new_coll_root.name].color_tag = f"COLOR_0{color_id}"
        elif self.coll_color_prop == "CURRENT":
            bpy.data.collections[new_coll_root.name].color_tag = active_coll_color
        else:
            bpy.data.collections[new_coll_root.name].color_tag = self.coll_color_prop

        # # store into library collection (user's choice)
        # bpy.ops.object.select_all(action='DESELECT')
        # new_obj = bpy.data.objects[new_coll_root.name].copy() 
        # bpy.context.scene.collection.objects.link(new_obj) 

        # create scene library and link new collection in it
        create_libraryScene_func(new_coll_name)

        # store in asset browser
        if storeAsset_prop:
            storeIn_AssetBrowser_func(new_coll_name,blender_version)

        # show informations
        print("selected_obj : " + str(stored_obj))
        print("new_coll_name : " + str(new_coll_name))

        print(f"\n {separator} {Addon_Name} - {tool_f} Finished {separator} \n")
        
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)    

# create operator UPPER_OT_lower and idname = upper.lower       
class OBJECT_OT_instcoll_instancecollectiontosel(bpy.types.Operator):
    bl_idname = 'object.instcol_instancecollectiontosel'
    bl_label = "Get collection back"
    bl_description = "Get back the original collection from the library. Right now, only works with the first selected object, and won't work if the original collection is already in the scene."
    bl_options = {"REGISTER", "UNDO"}

    keeptheInstColl_prop : bpy.props.BoolProperty(name = 'Keep the instance collection',description = "if checked, the instance collection won't be removed",default = True)
    
    def execute(self, context):
        print(f"\n {separator} Begin {Addon_Name} - {tool_i} {separator} \n")

        obj_sel = bpy.context.selected_objects
        wanted_obj = obj_sel[0]

        #print(obj_sel)
        #print(obj_sel[0].type)

        # replace instance collection by the original collection
        if wanted_obj.type == 'EMPTY' and wanted_obj.instance_type == 'COLLECTION':
            #print(wanted_obj.instance_collection)
            if wanted_obj.instance_collection.name not in bpy.context.scene.collection.children.keys(): # check if this is the only occurence
                bpy.context.scene.collection.children.link(bpy.data.collections[wanted_obj.instance_collection.name])
                
                # remove object
                if self.keeptheInstColl_prop == False:
                    bpy.data.objects.remove(wanted_obj, do_unlink=True)
        else:
            print('selected object is not and instance collection')

        print(f"\n {separator} {Addon_Name} - {tool_i} Finished {separator} \n")        
        return {"FINISHED"}

# create operator UPPER_OT_lower and idname = upper.lower
class OBJECT_OT_instcoll_updateAssetBrowser(bpy.types.Operator):
    bl_idname = 'object.instcol_updateassetbrowser'
    bl_label = "Update Asset Browser"
    bl_description = "Update asset browser from the library scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        print(f"\n {separator} Begin {Addon_Name} - {tool_f} {separator} \n")

        user_label_pref = bpy.context.preferences.addons[__name__].preferences.user_label_pref
        user_labelPos_pref = bpy.context.preferences.addons[__name__].preferences.user_labelPos_pref

        # check all collections from the selected library scene
        for coll in bpy.context.scene.collection.children:
            store = False
            if user_labelPos_pref == "Prefix":
                if coll.name.startswith(user_label_pref):
                    store = True
            elif user_labelPos_pref == "Suffix":
                if coll.name.endswith(user_label_pref):
                    store = True
            # for collections well named :
            if store:
                storeIn_AssetBrowser_func(coll.name,blender_version)

        print(f"\n {separator} {Addon_Name} - {tool_f} Finished {separator} \n")
        return {"FINISHED"}

# create operator UPPER_OT_lower and idname = upper.lower
class OBJECT_OT_instcoll_renameselection(bpy.types.Operator):
    bl_idname = 'object.instcol_renameselection'
    bl_label = "Rename selection from its data"
    bl_description = "Rename objects regarding to its meshes, or library regarding to its instance collection"
    bl_options = {"REGISTER", "UNDO"}
    
    # redo panel = user interraction
    rename_option = [
        ("Data blocks > Objects","Data rename Object","Data blocks rename objects. The main behavior",1),
        ("Objects > Data blocks","Object rename Data","Objects rename Data. WARNING : may cause strange behavior if instanced data !!",2),        
    ]
    rename_dataToObject : bpy.props.EnumProperty(
            items = rename_option,
            name = "Rename behavior",
            description = "conforms names between datas and objects",
            default=1,
    )
    
    def execute(self, context):
        print(f"\n {separator} Begin {Addon_Name} - {tool_a} {separator} \n")
        
        sel_obj = bpy.context.selected_objects
                
        if len(sel_obj) > 0:
            if self.rename_dataToObject == "Data blocks > Objects":
                rename_from_datablock_func(bpy.context.selected_objects,False)
            elif self.rename_dataToObject == "Objects > Data blocks":
                for obj in sel_obj:
                    if obj.type == 'MESH':
                        bpy.data.objects[obj.name].data.name = bpy.data.objects[obj.name].name
                    elif obj.type == 'EMPTY' and obj.instance_type == 'COLLECTION':
                        if obj.instance_collection != None:
                            bpy.data.objects[obj.name].instance_collection.name = bpy.data.objects[obj.name].name

        print(f"Renaming done on {sel_obj}")
        print(f"\n {separator} {Addon_Name} - {tool_a}  Finished {separator} \n")            
        
        return {"FINISHED"}

# # create operator UPPER_OT_lower and idname = upper.lower
# class OBJECT_OT_instcoll_collectioncenter(bpy.types.Operator):
#     bl_idname = 'object.instcol_collectioncenter'
#     bl_label = "Set collections center from selection"
#     bl_description = "Each collection center will be set by the center of the selection"
#     bl_options = {"REGISTER", "UNDO"}
    
#     z_onFloor : bpy.props.BoolProperty(
#             name = "Z centered ",
#             description = "Z coordinates centered or at 0",
#             default=False,    
#     )
    
#     def execute(self, context):             
#         print(f"\n {separator} Begin {Addon_Name} - {tool_b} {separator} \n")
                
#         # get media loc x, y and z from selection
#         sel_set = bpy.context.selected_objects
        
#         # create collection list from selected objects
#         cols_from_sel = []
#         for obj in sel_set:
#             if obj.users_collection != (bpy.data.scenes[bpy.context.scene.name].collection,):
#                 if bpy.data.objects[obj.name].users_collection[0].name not in cols_from_sel:
#                     cols_from_sel.append(bpy.data.objects[obj.name].users_collection[0].name)
        
#         sel_loc_x = []
#         sel_loc_y = []
#         sel_loc_z = []
        
#         # create selection offset from each collection
#         for col in cols_from_sel:
#             sel_loc_x.clear()
#             sel_loc_y.clear()
#             sel_loc_z.clear()
#             for obj in sel_set and bpy.data.collections[col].objects.values():
#                 sel_loc_x.append(obj.location.x)
#                 sel_loc_y.append(obj.location.y)
#                 sel_loc_z.append(obj.location.z)
#             med_sel_x = mean(sel_loc_x)
#             med_sel_y = mean(sel_loc_y)
#             med_sel_z = mean(sel_loc_z)
#             if self.z_onFloor == False:
#                 coord_z = 0
#             else:
#                 coord_z = med_sel_z
#             bpy.data.collections[col].instance_offset = (med_sel_x,med_sel_y,coord_z)
 
#         print(f"offset collection done on {cols_from_sel}")
#         print(f"\n {separator} {Addon_Name} - {tool_b} Finished {separator} \n")
 
#         return {"FINISHED"}

# # create operator UPPER_OT_lower and idname = upper.lower        
# class OBJECT_OT_instcoll_meshtocollection(bpy.types.Operator):
#     bl_idname = 'object.instcol_meshtocollection'
#     bl_label = "Convert Mesh to Instance Collection"
#     bl_description = "Convert selected meshes to empty instance collection"
#     bl_options = {"REGISTER", "UNDO"}

#     def execute(self, context):
#         print(f"\n {separator} Begin {Addon_Name} - {tool_c} {separator} \n")
            
#         # get list of selected objects
#         sel_set = []
#         meshes_sel_set = []
#         for obj in bpy.context.selected_objects:
#             sel_set.append(obj)
#             if obj.type == 'MESH':
#                 meshes_sel_set.append(obj)
        
#         # Convert objects to exmpty instance collection
#         if len(meshes_sel_set) > 0 :
#             sel_set = []
#             for obj in meshes_sel_set:
#                 bpy.ops.object.add()
#                 empty = bpy.context.active_object
#                 empty.name = obj.name
#                 empty.matrix_world = obj.matrix_world
#                 bpy.data.objects[empty.name].instance_type = 'COLLECTION'
#                 empty.instance_collection = None
#                 bpy.data.objects.remove(obj, do_unlink=True)
#                 sel_set.append(empty)     
                
#         # get selection from before
#         if len(sel_set) > 0:
#             for obj in sel_set:
#                 obj.select_set(True)
        
#         print(f"Meshes converted in instance collections : {sel_set}")
#         print(f"\n {separator} {Addon_Name} - {tool_c} Finished {separator} \n")
        
#         return {"FINISHED"}
        


# list all classes
classes = (
    INSTCOLL_Preferences,
    INSTCOLL_properties,
    VIEW3D_PT_instcoltoolbox_all,
    # VIEW3D_PT_instcoladdtools,
    OBJECT_OT_instcoll_renameselection,
    #OBJECT_OT_instcoll_collectioncenter,
    #OBJECT_OT_instcoll_meshtocollection,
    OBJECT_OT_instcoll_seltoinstancecollection,
    OBJECT_OT_instcoll_colltoinstancecollection,
    OBJECT_OT_instcoll_instancecollectiontosel,
    OBJECT_OT_instcoll_updateAssetBrowser,
    )

# register classes
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.instanceColl_props = bpy.props.PointerProperty (type = INSTCOLL_properties)

#unregister classes 
def unregister():    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.instanceColl_props

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.simple_operator('INVOKE_DEFAULT')
   

### Left to do : ###
#    sel collection center bugged
# collection to instance collection n'a pas fonctionné sur le tree B (voir le replayS)
# snap to ground (avec mesg density)
# bug sur randomized areas crées plusieurs fois (base et sub coll)
# bug sur library (qui ne veut pas prendre autre chose)