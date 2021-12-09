bl_info = {
    "name": "Camera addon",
    "blender": (2, 82, 0),
	"author": "Yuri Romanov",
    "category": "Camera"
}

import bpy
from bpy.types import Operator, Menu, Panel, PropertyGroup, PointerProperty, Object

#--------------------------------------------------------------------------------------
# F E A T U R E S
#--------------------------------------------------------------------------------------

# Создаем и задаем базовые значения положения камеры
class Camera_Custom_Resolution_Settings(PropertyGroup):
    Custom_Horizontal_Resolution: bpy.props.IntProperty(
        name="Custom Horizontal Resolution",
        description="Custom Horizontal Resolution",
        default = 1920)
        
    Custom_Vertical_Resolution: bpy.props.IntProperty(
        name="Custom Vertical Resolution",
        description="Custom Vertical Resolution",
        default = 1080)

# Функция для установки кастомного положения камеры
def SetCameraCustomResolution(self, context):
    context.scene.render.resolution_x = context.active_object.camera_custom_resolution_settings_pointer_prop.Custom_Horizontal_Resolution
    context.scene.render.resolution_y = context.active_object.camera_custom_resolution_settings_pointer_prop.Custom_Vertical_Resolution

# Выключить просмотр от выбранной камеры
class CameraViewOff(bpy.types.Operator):
    bl_idname = 'cameras.camera_view_off'
    bl_label = 'Camera View Off'
    bl_description = "Camera View Off"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()
    
    def execute(self,context):
        context.area.spaces[0].region_3d.view_perspective='PERSP'

        return{'FINISHED'}

# Выровнять камеру по текущему положению
class AlignSelectedCameraToView(bpy.types.Operator):
    bl_idname = 'cameras.align_selected_to_view'
    bl_label = 'Align Selected to View'
    bl_description = "Align selected camera to view"
    bl_options = {'UNDO'}

    def execute(self,context):
        if context.object:
            if context.area.spaces[0].region_3d.view_perspective == 'CAMERA': #если положение совпадает, то завершаем
                return {'FINISHED'}
            else:
                ob = context.object
                if ob.type == 'CAMERA': #выравниваем камеру по виду
                    scene = bpy.context.scene
                    currentCameraObj = bpy.data.objects[bpy.context.active_object.name]
                    scene.camera = currentCameraObj
                    bpy.ops.view3d.camera_to_view()

        return{'FINISHED'}

# Добавляем новую камеру от вида
class NewCameraFromView(bpy.types.Operator):
    bl_idname = 'cameras.new_from_view'
    bl_label = 'New Camera From View'
    bl_description = "Create a new camera from view"
    bl_options = {'UNDO'}

    def execute(self,context):
        if context.area.spaces[0].region_3d.view_perspective == 'CAMERA':
            context.area.spaces[0].region_3d.view_perspective='PERSP'
        bpy.ops.object.camera_add()
        scene = bpy.context.scene
        currentCameraObj = bpy.data.objects[bpy.context.active_object.name]
        scene.camera = currentCameraObj
        bpy.ops.view3d.camera_to_view()

        return{'FINISHED'}

# Опции рендеринга: установки
def update_render_engine(self, context):
    selected_engine = context.scene.set_render_engine
    
    if selected_engine == render_engine_options[0][0]:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    if selected_engine == render_engine_options[1][0]:
        bpy.context.scene.render.engine = 'CYCLES'

render_engine_options = [
        ("eevee", "EEVEE", ""),
        ("cycles", "CYCLES", "")]

bpy.types.Scene.set_render_engine = bpy.props.EnumProperty(
    items=render_engine_options,
    description="Set render engine",
    default= "eevee",
    update = update_render_engine)

# Типы по которым проводим сортировку
sorting_cameras_options = [
        ("alphabetically", "Alphabetically", ""),
        ("by_collections", "By Collections", "")]

bpy.types.Scene.sort_cameras = bpy.props.EnumProperty(
    items=sorting_cameras_options,
    description="Sort cameras",
    default= "alphabetically")

# Включить просмотр от выбранной камеры(установить вид камеры)
class SetCameraView(bpy.types.Operator):
    bl_idname = 'cameras.set_view'
    bl_label = 'Set Camera View'
    bl_description = "Set View to this Camera"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        
        #перебираем возможные варианты положения камеры, если какой-то из них проходит, то выполняем прописанные действия
        if bpy.context.object.hide_get(view_layer=None) == True and bpy.context.object.hide_viewport == False:
            bpy.context.object.hide_set(False)
            bpy.ops.cameras.select(camera=self.camera)
            bpy.ops.view3d.object_as_camera()
            bpy.ops.view3d.view_center_camera()
            SetCameraCustomResolution(self, context)
            bpy.context.object.hide_set(True)
        elif bpy.context.object.hide_get(view_layer=None) == False and bpy.context.object.hide_viewport == True:
            bpy.context.object.hide_viewport = False
            bpy.ops.cameras.select(camera=self.camera)
            bpy.ops.view3d.object_as_camera()
            bpy.ops.view3d.view_center_camera()
            SetCameraCustomResolution(self, context)
            bpy.context.object.hide_viewport = True
        elif bpy.context.object.hide_get(view_layer=None) == True and bpy.context.object.hide_viewport == True:
            bpy.context.object.hide_set(False)
            bpy.context.object.hide_viewport = False
            bpy.ops.cameras.select(camera=self.camera)
            bpy.ops.view3d.object_as_camera()
            bpy.ops.view3d.view_center_camera()
            SetCameraCustomResolution(self, context)
            bpy.context.object.hide_set(True)
            bpy.context.object.hide_viewport = True
        else:
            bpy.ops.cameras.select(camera=self.camera)
            bpy.ops.view3d.object_as_camera()
            bpy.ops.view3d.view_center_camera()
            SetCameraCustomResolution(self, context)

        return{'FINISHED'}

# выбрать камеру
class SelectCamera(bpy.types.Operator):
    bl_idname = 'cameras.select'
    bl_label = 'Select Camera'
    bl_description = "Select camera"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        
        if context.object:
            if context.object.select_get():
                context.object.select_set(state=False)
        cam=bpy.data.objects[self.camera]
        cam.select_set(state=True)
        context.view_layer.objects.active = cam
        context.scene.camera=cam
        
        #перебираем возможные варианты положения камеры, если какой-то из них проходит, то выполняем прописанные действия
        if bpy.context.object.hide_get(view_layer=None) == True and bpy.context.object.hide_viewport == False:
            bpy.context.object.hide_set(False)
            SetCameraCustomResolution(self, context)
            bpy.context.object.hide_set(True)
        elif bpy.context.object.hide_get(view_layer=None) == False and bpy.context.object.hide_viewport == True:
            bpy.context.object.hide_viewport = False
            SetCameraCustomResolution(self, context)
            bpy.context.object.hide_viewport = True
        elif bpy.context.object.hide_get(view_layer=None) == True and bpy.context.object.hide_viewport == True:
            bpy.context.object.hide_set(False)
            bpy.context.object.hide_viewport = False
            SetCameraCustomResolution(self, context)
            bpy.context.object.hide_set(True)
            bpy.context.object.hide_viewport = True
        else:
            SetCameraCustomResolution(self, context)
        
        return{'FINISHED'}


# Создаем маркер камеры
class BindCameraToMarker(bpy.types.Operator):
    bl_idname = 'cameras.bind_to_marker'
    bl_label = 'Bind Camera to Marker'
    bl_description = "Bind camera to marker at current frame"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        
        #cохраняем маркеры сцены        
        tm = bpy.context.scene.timeline_markers
        #сохраняем текущий кадр
        cur_frame = context.scene.frame_current
        #сохраняем маркер на текущем кадре
        frame_markers = [marker for marker in tm if marker.frame == cur_frame]
        
        #если маркер не существует, то создаем его
        if len(frame_markers) == 0:
            new_marker = tm.new(self.camera, frame = cur_frame)
            new_marker.camera = bpy.data.objects[self.camera]
        elif len(frame_markers) >= 1: #если маркер есть, то удаляем
            for marker in frame_markers:
                tm.remove(marker)
            new_marker = tm.new(self.camera, frame = cur_frame)
            new_marker.camera = bpy.data.objects[self.camera]
        
        return{'FINISHED'}

# Удаляем маркер камеры
class Delete_Camera_Marker(bpy.types.Operator):
    bl_idname = 'cameras.delete_camera_marker'
    bl_label = 'Delete Camera Marker'
    bl_description = "Delete camera marker at current frame"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        
        #cохраняем маркеры сцены
        tm = bpy.context.scene.timeline_markers 
        #сохраняем текущий кадр
        cur_frame = context.scene.frame_current
        #сохраняем маркер на текущем кадре
        frame_markers = [marker for marker in tm if marker.frame == cur_frame]
        
        #проверяем является ли выбранные кадры маркированными
        for marker in frame_markers:
            if marker.name == self.camera:
                tm.remove(frame_markers[0])

        return{'FINISHED'}

# Удаляем камеру
class DeleteCamera(bpy.types.Operator):
    bl_idname = 'cameras.delete'
    bl_label = 'Delete Camera'
    bl_description = "Delete camera"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()


    #удаляем объекты камеры
    def execute(self,context):
        cam=bpy.data.objects[self.camera] 
        bpy.data.objects.remove(cam)
        
        
        #удаляем маркеры камеры
        tm = bpy.context.scene.timeline_markers
        for marker in tm:
            if marker.name == self.camera:
                 tm.remove(marker)
        
        return{'FINISHED'}

# Панель расширеных настроек
class PanelButton_CameraSettings(bpy.types.Operator):
    bl_idname = "camera.settings"
    bl_label = "Camera Settings"
    bl_description = "Select camera"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        pass

    def draw(self, context):
        layout = self.layout
        
        cam = bpy.context.object.data
        layout.label(text="RENDER SETTINGS", icon="RESTRICT_RENDER_OFF")
        col = layout.column(align=False)
        row = col.row()
        row.prop(cam, "type", text="")

        if cam.type == 'PERSP':
            precol = col.column(align=True)
            precolbox = precol.box()
            precolbox.prop(cam, "lens_unit", text="")
            if cam.lens_unit == 'MILLIMETERS':
                precolbox.prop(cam, "lens", text="Focal")
            elif cam.lens_unit == 'FOV':
                precolbox.prop(cam, "angle", text="Field of View")
            
        elif cam.type == 'ORTHO':
            precol = col.column(align=True)
            precol.prop(cam, "ortho_scale", text="Scale")
            
        elif cam.type == 'PANO':
            engine = context.engine
            if engine == 'CYCLES':
                ccam = cam.cycles
                row.prop(ccam, "panorama_type", text="")
                
                if ccam.panorama_type == 'FISHEYE_EQUIDISTANT':
                    row = col.row()
                    row.prop(ccam, "fisheye_fov", text="Field of View")
                    
                elif ccam.panorama_type == 'FISHEYE_EQUISOLID':
                    row = col.row()
                    row.prop(ccam, "fisheye_lens", text="Lens")
                    row.prop(ccam, "fisheye_fov", text="FOV")
                    
                elif ccam.panorama_type == 'EQUIRECTANGULAR':
                    row = col.row()
                    row.prop(ccam, "latitude_min", text="Latitude Min")
                    row.prop(ccam, "longitude_min", text="Longitude Min")
                    row = col.row()                            
                    row.prop(ccam, "latitude_max", text="Latitude Max")
                    row.prop(ccam, "longitude_max", text="Longitude Max")
        
        col = layout.column(align=True)
        precol = col.column(align=True)
        precolbox = precol.box()
        precolbox.label(text="Shift:")
        precolbox.prop(cam, "shift_x", text="Horizontal")
        precolbox.prop(cam, "clip_start", text="Start")
        precol = col.column(align=True)
        precolbox = precol.box()
        precolbox.label(text="Clip:")
        precolbox.prop(cam, "shift_y", text="Vertical")
        precolbox.prop(cam, "clip_end", text="End")
        col = layout.column(align=True)
        precol = col.column(align=True)
        precolbox = precol.box()
        precolbox.label(text="Custom Resolution:")
        if bpy.context.object.hide_get(view_layer=None) == True or bpy.context.object.hide_viewport == True:
            precolbox.alert =True
            precolbox.label(text="Unhide Camera in viewport to setup resolution", icon= "ERROR")
        else:
            precolbox.prop(context.active_object.camera_custom_resolution_settings_pointer_prop, "Custom_Horizontal_Resolution", text="Horizontal")
            precolbox.prop(context.active_object.camera_custom_resolution_settings_pointer_prop, "Custom_Vertical_Resolution", text="Vertical")
        
    def invoke(self, context, event):
        
        if context.object:
            if context.object.select_get():
                context.object.select_set(state=False)
        cam=bpy.data.objects[self.camera]
        cam.select_set(state=True)
        context.view_layer.objects.active = cam
        context.scene.camera=cam

        if bpy.context.object.hide_get(view_layer=None) == True and bpy.context.object.hide_viewport == False:
            bpy.context.object.hide_set(False)
            SetCameraCustomResolution(self, context)
            bpy.context.object.hide_set(True)
        elif bpy.context.object.hide_get(view_layer=None) == False and bpy.context.object.hide_viewport == True:
            bpy.context.object.hide_viewport = False
            SetCameraCustomResolution(self, context)
            bpy.context.object.hide_viewport = True
        elif bpy.context.object.hide_get(view_layer=None) == True and bpy.context.object.hide_viewport == True:
            bpy.context.object.hide_set(False)
            bpy.context.object.hide_viewport = False
            SetCameraCustomResolution(self, context)
            bpy.context.object.hide_set(True)
            bpy.context.object.hide_viewport = True
        else:
            SetCameraCustomResolution(self, context)

        wm = context.window_manager
        return wm.invoke_popup(self)


# Основная панель
def common_draw(self,layout,context):
    #подфункция для сортировки коллекций
    def coll_rec(coll, clist): #передаем коллекции и список
        if coll.children: #если существуют "дети" этой коллекции
            for child in coll.children: #помещаем каждого потомка в эту же функцию, для поиска следующих возможно существующих потомков
                coll_rec(child, clist) 
        cams=[cam.name for cam in coll.objects if cam.type=='CAMERA'] #находим только камеры из всех объектов
        if cams:
            cams.sort(key=str.lower) #проводим сортировку
            clist.append((coll.name, cams)) #сохраняем в список название коллекции и сам объект(камеру)

    tm = bpy.context.scene.timeline_markers #обращаемся к временным маркерам
    cur_frame = context.scene.frame_current #сохраняем текущий кадр
    frame_markers = [marker for marker in tm if marker.frame == cur_frame] # проходим циклом по временным маркерам и сохраняем тот, который равен текущему

    box = layout
    row = box.row(align=True) #помещаем в разные ящейки
    row.scale_x = 2.5 #задаем размер
    row.scale_y = 1
    row.operator("render.render", text="", icon="RENDER_STILL") #создаем кнопку для рендера картинки
    row.operator("render.render", text="", icon="RENDER_ANIMATION").animation=True #cоздаем кнопку для рендара множества кадров
    row.operator("render.view_show", text="", icon="IMAGE_DATA") #показать скрыть рендер
    if ((context.area.spaces[0].region_3d.view_perspective == 'PERSP' or context.area.spaces[0].region_3d.view_perspective == 'ORTHO')
    and context.area.spaces.active.use_render_border == False):
        row.operator("view3d.render_border", text="", icon="BORDERMOVE")
    elif ((context.area.spaces[0].region_3d.view_perspective == 'PERSP' or context.area.spaces[0].region_3d.view_perspective == 'ORTHO')
    and context.area.spaces.active.use_render_border == True):
        row.alert = True #Вызывает красную подсветку
        row.operator("view3d.clear_render_border", text="", icon="BORDERMOVE")
        
    if context.area.spaces[0].region_3d.view_perspective == 'CAMERA' and bpy.data.scenes["Scene"].render.use_border == False:
        row.operator("view3d.render_border", text="", icon="BORDERMOVE")
    if context.area.spaces[0].region_3d.view_perspective == 'CAMERA' and bpy.data.scenes["Scene"].render.use_border == True:
        row.alert = True #Вызывает красную подсветку
        row.operator("view3d.clear_render_border", text="", icon="BORDERMOVE") #очищаем выбранный регион
    box.separator()  #добавляем пустую область для "красоты"
    column = box.column(align=True)
    column.prop(context.scene, "set_render_engine", text="", expand=False) #вызываем список с типами рендеров с виде выплывающего списка
    box.separator() #добавляем пустую область для "красоты"
    row = box.column(align=False)
    boxframe = row.box()
    boxframe.operator("cameras.new_from_view", text="Add Camera to View", icon="ADD") # добавляет новую камеру на сцену
    boxframe.operator("cameras.align_selected_to_view", text="Align Selected to View", icon="CON_CAMERASOLVER") #перемещаем выбранную камеру на положение, в которым вы находитесь
    box.separator() #добавляем пустую область для "красоты"
    row = box.row(align=True) #строка с объекдинением кнопок
    row.prop(context.scene, "sort_cameras", text=" ", expand=True) # вызываем кнопки сортировки камер
    boxframe = box.box() #помещаем текущий бокс в другой
    boxframecolumn = boxframe.column()
    sort_option = context.scene.sort_cameras #помещаем значение в переменную
    if sort_option == sorting_cameras_options[0][0]:
        cam_list=[cam.name for cam in context.scene.collection.all_objects if cam.type=='CAMERA'] #ищем объекты типа "камера"
        cam_list.sort(key=str.lower) #сортируем список
        if not cam_list: #если нет ни одной камеры
            row = boxframecolumn.row(align=True)
            row.alignment = "CENTER"
            row.alert = True #Вызывает красную подсветку
            row.label(text="No cameras in this scene", icon= "ERROR") # Выводим сообщение с иконкой 
        else:
            for cam in cam_list: #цикл по списку камер
                row = boxframecolumn.row(align=True)
                row.scale_x = 2 #объекдиняем кнопки в боксе
                row.operator("cameras.camera_view_off"  #выбирает камеры и сменяет иконоки 
                    if context.area.spaces[0].region_3d.view_perspective == 'CAMERA' 
                    and bpy.context.space_data.camera is bpy.context.scene.objects[cam] else "cameras.set_view",
                    text=cam, icon="CHECKBOX_HLT"
                    if bpy.context.space_data.camera is bpy.context.scene.objects[cam]
                    and context.object.type == 'CAMERA'
                    and context.area.spaces[0].region_3d.view_perspective == 'CAMERA'
                    else "CHECKBOX_DEHLT").camera=cam
                row.operator("cameras.delete_camera_marker" #добавляем кнопку, которая добавляет маркер на таймлайн
                    if len(frame_markers) >= 1 and frame_markers[0].name == cam else "cameras.bind_to_marker",
                    text="", icon="MARKER_HLT" if len(frame_markers) >= 1 and frame_markers[0].name == cam else "MARKER").camera=cam
                row.operator("cameras.delete", text="", icon="PANEL_CLOSE").camera=cam #кнопка "удаляем камеру"
                row.operator("camera.settings", text="", icon="PREFERENCES").camera=cam # кнопка "настройки камеры расширеные"
                
    elif sort_option == sorting_cameras_options[1][0]: # сортируем по коллекциям
        collcamlist=[] #список для имен коллекций и объектов камер
        master_coll = context.scene.collection #сохраняем мастер коллекцию 
        coll_rec(master_coll, collcamlist) # ищем все существующие камеры в коллекциях и сохраняем их имена
        collcamlist.sort()  # проводим сортировку полученного списка
        if not collcamlist: ##если нет ни одной камеры
            row = boxframecolumn.row(align=True)
            row.alignment = "CENTER"
            row.alert = True
            row.label(text="No cameras in this scene", icon= "ERROR") #выводим, что камер нет
        else:
            for coll in collcamlist:
                boxframecolumn.label(text=coll[0]) # выводим текстом название коллекции
                for cam in coll[1]: #добавляем кпонки камер
                    row = boxframecolumn.row(align=True)
                    row.scale_x = 2 #объекдиняем кнопки в боксе
                    row.operator("cameras.camera_view_off"
                        if context.area.spaces[0].region_3d.view_perspective == 'CAMERA'
                        and bpy.context.space_data.camera is bpy.context.scene.objects[cam] else "cameras.set_view",
                        text=cam, icon="CHECKBOX_HLT"
                        if bpy.context.space_data.camera is bpy.context.scene.objects[cam]
                        and context.object.type == 'CAMERA'
                        and context.area.spaces[0].region_3d.view_perspective == 'CAMERA'
                        else "CHECKBOX_DEHLT").camera=cam
                    row.operator("cameras.delete_camera_marker" #добавляем кнопку, которая добавляет маркер на таймлайн
                        if len(frame_markers) >= 1 and frame_markers[0].name == cam else "cameras.bind_to_marker",
                        text="", icon="MARKER_HLT" if len(frame_markers) >= 1 and frame_markers[0].name == cam else "MARKER").camera=cam
                    row.operator("cameras.delete", text="", icon="PANEL_CLOSE").camera=cam #кнопка "удаляем камеру"
                    row.operator("camera.settings", text="", icon="PREFERENCES").camera=cam # кнопка "настройки камеры расширеные"



class panel3(bpy.types.Panel):
    bl_idname = "panel.panel3"
    bl_label = "My Cameras"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Camera Setup'
    
    def draw(self, context):
        layout = self.layout # Определяет структуру панели в пользовательском интерфейсе
        box = layout.column(align=True) #меняем панель на колонки с выравниванием
        box.separator()
        common_draw(self, box, context)
        
    def execute(self, context):
        self.report({'INFO'}, self.my_enum)
        return {'FINISHED'}

#регистрация классов

classes = (
    Camera_Custom_Resolution_Settings,
    CameraViewOff,
    AlignSelectedCameraToView,
    NewCameraFromView,
    SetCameraView,
    SelectCamera,
    BindCameraToMarker,
    Delete_Camera_Marker,
    DeleteCamera,
    PanelButton_CameraSettings,
    panel3,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    Object.camera_custom_resolution_settings_pointer_prop = bpy.props.PointerProperty(type = Camera_Custom_Resolution_Settings)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
    
    del Object.Pointer_Camera_Custom_Resolution_Settings



if __name__ == "__main__":
    register()