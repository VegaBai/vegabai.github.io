"""
SnowWorld.py

Using particles to generate a beautiful snowy scene.

__author__ = "Vega Bai"
__copyright__ = "Copyright 2015, Vega Bai"
__version__ = "1.0.5"
__maintainer__ = "Vega Bai"
__email__ = "vegabeyond@gmail.com"
__status__ = "Updating"

logs: 
    v1.0.5: 12-19-2015, add error captions
    v1.0.4: 12-19-2015, add collisions; delete animation length option
    v1.0.3: 12-16-2015, add particle render type - cloud
    v1.0.2: 12-9-2015, add texture sequence
    v1.0.1: 12-2-2015, add log function
    
instructions:
    1. click on the plane
    2. click 'Select Start Plane' button
    3. if you want to use a specific image as snowflake texture, browse and select the image, then turn on the 'Use file as texture' checkbox. if you don't turn on the checkbox, the particle will be rendered as white cloud type
    4. if you want to use more than one image to texture different particles, then turn on the 'Use file Sequence' checkbox. then the file browsered just now will be set as the start of the file sequence. make sure to name the textures in 'image.n' format. for example, 'snow.1'
    5. set values of 'Average Size', 'Density', 'MaxHeight'
    6. set values of 'Direction Vector'
    7. if you want to make collisions between other objects and the particles, select those objects and then click 'Select Object Collide With' button, and turn on 'Make Collision' checkbox 
    8. click 'Run' to start generating the snowy scene

"""

import pymel.core as pm
import random
import logging
import os

FILE_PATH_OV = 'filePathOv'  # save the file path
snowPath = ''

# setup a logger
logger = logging.getLogger(__name__)
hdlr = logging.handlers.RotatingFileHandler('SnowWorldLog.txt', maxBytes = 100000)
hdlr.setLevel(logging.DEBUG)
format = ('%(asctime)s, module=%(module)s, message=%(message)s')
formatter = logging.Formatter(format)
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)


def run(sliderSize, sliderDensity, sliderHeight, textSequence, ckboxTexture, ckboxSequence, ckboxCover, directionX, directionY, directionZ, snowPieceBrowser):
    '''
    This function is the main function to generate the snowy scene.
    
    Args:
        avgSize from sliderSize: The average size of all snow piece
        density from sliderDensity: The density of the snow
        maxDistance from sliderHeight: The highest distance the user want the snow to fall
        snowTexture from ckboxTexture: Whether using the texture for snowflakes
        snowSequence from textSequence: The length of the sequence of images as texture
        directionX: directionX of gravity field
        directionY: directionX of gravity field
        directionZ: directionX of gravity field
        
        coverFlag(coverObj) from ckboxCover: Decide whether the snow will cover the models and which models to cover
        windFlag(windDirection, windStrength): Decide whether there are winds and the directions and strength
        
    GLobal variables used:
        startArea: The surface area the user want the snow fall from
        snowPath: The file path of the snowflake texture
        coverObj: The objects the particles will make collision with
        
    Result: 
        a generated snowy scene animation
        
    Return: 
        none
    
    '''
    ## check whether the user has selected the start Area    
    if isset('startArea') == 0:        
        logger.error('Please choose a plane to start snow!')
        pm.PopupError('Please choose a plane to start snow!')
        return
    ## check whether the user has selected the objects to make collision with
    if ckboxCover.getValue():
        if isset('coverObj') == 0:
            logger.error('Please select the objects to make collision with!')
            pm.PopupError('Please select the objects to make collision with!')
            return
    ## check whether the user has selected files for textures
    snowPath = snowPieceBrowser.getText()
    if ckboxTexture.getValue():
        if snowPath == '':            
            logger.error('Please select the images for textures!')
            pm.PopupError('Please select the images for textures!')
            return            
        
    logger.info('Start generating the snowy scene')

    snowSize = sliderSize.getValue()
    snowDensity = sliderDensity.getValue()
    snowHeight = sliderHeight.getValue()
    
    snowTexture = ckboxTexture.getValue()
    snowSequenceTmp = textSequence.getText()
    snowSequence = int(snowSequenceTmp)
    gdXs = directionX.getText()
    gdYs = directionY.getText()
    gdZs = directionZ.getText()
    
    gdX = float(gdXs)
    gdY = float(gdYs)
    gdZ = float(gdZs)

    pm.playbackOptions(ps = 0.4)
    
    offsetSize = snowSize * 0.3
    minSize = snowSize - offsetSize
    maxSize = snowSize + offsetSize
    
    
    startFace = startArea
    emitter1 = pm.emitter(startFace, sro = True, type = 'surface', rate = snowDensity, minDistance = 0.5, mxd = 1)
    particle_snow2 = pm.particle()
    pm.connectDynamic(particle_snow2, em = emitter1)
    
    ## using image textures for particles
    if ckboxTexture.getValue():
        logger.info(' particle render type: sprite ')
        pm.setAttr('%s.particleRenderType'%particle_snow2[0], 5)
        pm.addAttr(particle_snow2[1], internalSet = True, longName = 'spriteTwist', attributeType = 'float', minValue = -180, maxValue = 180, defaultValue = 0.0)
        pm.addAttr(particle_snow2[1], internalSet = True, ln = 'spriteScaleX', dv = 0.2)
        pm.addAttr(particle_snow2[1], internalSet = True, ln = 'spriteScaleY', dv = 0.2)
        pm.addAttr(particle_snow2[1], internalSet = True, ln = 'spriteNum', at = 'long', dv = 1)
        pm.addAttr(particle_snow2[1], internalSet = True, ln = 'useLighting', at = 'bool',dv = False)
    
        shader2 = pm.shadingNode('lambert', asShader = True)
        file_node2 = pm.shadingNode('file', asTexture = True)
        pm.setAttr('%s.fileTextureName'%file_node2, snowPath, type = 'string')
        shading_group2 = pm.sets(renderable = True, noSurfaceShader = True, empty = True)
        pm.setAttr('%s.ambientColor'%shader2, 1.0, 1.0, 1.0, type = 'double3')
        pm.connectAttr('%s.outColor'%shader2, '%s.surfaceShader'%shading_group2, force = True)
        pm.connectAttr('%s.outColor'%file_node2, '%s.color'%shader2, force = True)
        pm.connectAttr('%s.outTransparency'%shader2, '%s.surfaceShader'%shading_group2, force = True)
        pm.connectAttr('%s.outTransparency'%file_node2, '%s.transparency'%shader2, force = True)
        pm.sets(shading_group2, e = True, forceElement = '%s'%particle_snow2[0])
        
        if ckboxSequence.getValue():
            pm.setAttr('%s.useFrameExtension'%file_node2, 1)
            pm.setAttr('%s.useHardwareTextureCycling'%file_node2, 1)
            pm.setAttr('%s.endCycleExtension'%file_node2, snowSequence)
         
        pm.addAttr(particle_snow2[1], dataType = 'doubleArray', ln = 'spriteScaleXPP')
        pm.addAttr(particle_snow2[1], dataType = 'doubleArray', ln = 'spriteScaleXPP0')
        pm.addAttr(particle_snow2[1], dataType = 'doubleArray', ln = 'spriteScaleYPP')
        pm.addAttr(particle_snow2[1], dataType = 'doubleArray', ln = 'spriteScaleYPP0')
        pm.addAttr(particle_snow2[1], dataType = 'doubleArray', ln = 'spriteTwistPP')
        pm.addAttr(particle_snow2[1], dataType = 'doubleArray', ln = 'spriteTwistPP0') 
        pm.dynExpression(particle_snow2[1], s = 'spriteScaleXPP = rand(%f,%f);\nspriteScaleYPP = spriteScaleXPP;\nspriteTwistPP = rand(0,30);'%(minSize, maxSize), c = True)
        
        if ckboxSequence.getValue():
            pm.addAttr(particle_snow2[1], dataType = 'doubleArray', ln = 'spriteNumPP')
            pm.addAttr(particle_snow2[1], dataType = 'doubleArray', ln = 'spriteNumPP0')
            pm.dynExpression(particle_snow2[1], s = 'spriteScaleXPP = rand(%f,%f);\nspriteScaleYPP = spriteScaleXPP;\nspriteTwistPP = rand(0,30);\nspriteNumPP = rand(0,%f);\nspriteNumPP = (spriteNumPP+1)%%%f;'%(minSize, maxSize, snowSequence, snowSequence+1), c = True) 
    ## don't using textures
    else:
        logger.info(' particle render type: cloud ')
        pm.setAttr('%s.particleRenderType'%particle_snow2[0], 8)
        pm.addAttr(particle_snow2[1], dataType = 'doubleArray', ln = 'radiusPP')
        pm.addAttr(particle_snow2[1], dataType = 'doubleArray', ln = 'radiusPP0')
        pm.addAttr(particle_snow2[1], dataType = 'vectorArray', ln = 'rgbPP')
        pm.addAttr(particle_snow2[1], dataType = 'vectorArray', ln = 'rgbPP0')        
        pm.dynExpression(particle_snow2[1], s = 'radiusPP = rand(%f,%f);\nrgbPP = <<1,1,1>>;'%(minSize, maxSize), c = True)
    
    ## if make collision
    if ckboxCover.getValue():
        for j in range(len(coverObj)):
            pm.collision(coverObj[j], particle_snow2[1], r = 0, f = 1)
    
    ## add gravity
    snowGravity = pm.gravity('%s'%particle_snow2[0], dx = gdX, dy = gdY, dz = gdZ, magnitude = 1.0)
    pm.connectDynamic('%s'%particle_snow2[0], f = snowGravity)    
    
    
    logger.info('Scene generation finished!')
    return

def  isset(v):
    '''
    This function is for check whether a variable is available.
    
    Args:
        v: the string name of the variable
    Returns:
        0: the variable is not set
        1: the variable is set
    '''
    try :  
        if (eval(v)):
            logger.info('%s defined correctly.'%v)
    except NameError:  
        return   0   
    else :  
        return   1 

def selectObj(selType):
    '''
    This function gets the selected object.
    
    Args:
        selType: decide which kind of object the function will return
            0 - object name
            1 - select start area
            2 - select cover objects
    
    Returns:
        object: the name of the selected object
    
    Raises:
        ValueError: will return nothing
    '''
    global snowPiece
    global startArea
    global startAreaIndex
    global coverObj

    selObj = pm.selected()
    
    ### judge if there is object selected
    if not selObj:
        pm.PopupError("No object selected!")
        logger.error('No object selected!')
        return
    
    ### select object
    if selType == 0:
        snowObj = selObj
        logger.info('obj OK: %s' %snowObj)
        return snowObj

    ### select plane that the snow starts
    elif selType == 1:
        startArea = selObj[0]
        logger.info('plane OK: %s' % startArea)
        return startArea
    
    ### select objects that the particle would collide with
    elif selType == 2:
        coverObj = selObj
        logger.info('cover objects OK: %s' % coverObj)
        return coverObj
    
    return
    
## two dunctions for browser the file    
def getPath(control):
    '''
    This function is to get the file path of a file from the file browser.
    
    Results:
        If success, run updatePath()
        If failure, return None
            
    Returns:
        None
            
    '''    
    source = pm.fileDialog2(fileMode = 1,
                            fileFilter = '*.png',
                            caption = 'Pick A File To Import'
                            )
    if source:
        # put browsed path into field
        control.setFileName(source[0])
        
        # run update on field
        updatePath(control)
    else:
        return None
    
def updatePath(control):
    '''
    This function gets the updated the file path.
    
    Results:
        save the new file path to optionVar[FILE_PATH_OV]
        
    Returns:
        none
        
    '''       
    # get the value of the field
    text = control.getText()
    path = text
    
    # save the optionVar
    pm.optionVar[FILE_PATH_OV] = path
    
    logger.info('FIle path loaded: %s'%path)
        
def ui():
    '''
    This is the main ui function of generating the snowy scene.
        
    Returns:
        none
        
    '''   
    winTitle = 'Snow World'
    winName = 'winSnowWorld'
    winWidth = 300
    winHeight = 260
    
    if pm.window(winName, exists = True):
        pm.deleteUI(winName)
    
    snowWin = pm.window(winName,
                       title = winTitle,
                       widthHeight = (winWidth, winHeight)
                       )
    colLayoutMain = pm.columnLayout(adj = True)
    

    ### select start area button
    buttonSelArea = pm.button(label = 'Select Start Plane',
                              width = 100,
                              command = pm.Callback(selectObj, 1)
                              )
    ### select single snow piece model dialog
    snowPieceBrowser = pm.textFieldButtonGrp(buttonLabel = 'Browser',
                                             label = 'Snow Piece to import:',
                                             columnWidth3 = (110, 50, 50),
                                             adj = 2,
                                             ann = 'Enter A File Path'
                                             )
    snowPieceBrowser.buttonCommand(pm.Callback(getPath, snowPieceBrowser))
    snowPieceBrowser.changeCommand(pm.Callback(updatePath, snowPieceBrowser))
    snowPiecePath = ''
    if FILE_PATH_OV in pm.optionVar:
        snowPiecePath = pm.optionVar[FILE_PATH_OV]    
    if snowPiecePath:
        snowPieceBrowser.setFileName(snowPiecePath)
    
    ### layout for texture checkbox
    rowLayoutCkBox = pm.rowLayout(nc = 2,
                                  cw2 = (120, 30),
                                  co2 = (20, 20),
                                  parent = colLayoutMain
                                  )     
    pm.text(label = ' ',
            font = 'fixedWidthFont',
            parent = rowLayoutCkBox
            )    
    #### checkbox for whether to use textures for snow pieces
    ckboxTexture = pm.checkBox(label = 'Use file as texture',
                               value= True, 
                               parent = rowLayoutCkBox
                               )   
    
    ### layout for texture sequence checkbox
    rowLayoutCkBox2 = pm.rowLayout(nc = 3,
                                    cw3 = (120, 40, 30),
                                    co3 = (20, 20, 20),
                                    parent = colLayoutMain
                                    ) 
    pm.text(label = 'Number of Files:',
            font = 'fixedWidthFont',
            parent = rowLayoutCkBox2
            )
    textSequence = pm.textField('Input',
                              tx = '1',
                              font = 'fixedWidthFont',
                              backgroundColor = (0, 0, 0),
                              parent = rowLayoutCkBox2
                              )
    #### checkbox for whether to use textures sequences
    ckboxSequence = pm.checkBox(label = 'Use file sequence',
                                value= True, 
                                parent = rowLayoutCkBox2
                                )      
    
    ### slider for average size of snowpiece
    sliderSize = pm.floatSliderGrp(label = 'Avg Size',
                                   field = True,
                                   minValue = 0.01,
                                   maxValue = 10.0,
                                   fieldMinValue = 0.01,
                                   fieldMaxValue = 10.0,
                                   value = 1,
                                   cw3 = (60, 40, 200),
                                   adj = 3,
                                   parent = colLayoutMain
                                   )
    
    ### slider for density of snow
    sliderDensity = pm.floatSliderGrp(label = 'Density',
                                      field = True,
                                      minValue = 0.1,
                                      maxValue = 5.0,
                                      fieldMinValue = 0.1,
                                      fieldMaxValue = 5.0,
                                      value = 1,
                                      cw3 = (60, 40, 200),
                                      adj = 3,
                                      parent = colLayoutMain
                                      )
    ### slider dor max height
    sliderHeight = pm.floatSliderGrp(label = 'Max Height',
                                     field = True,
                                     minValue = 1,
                                     maxValue = 100,
                                     fieldMinValue = 1,
                                     fieldMaxValue = 100,
                                     value = 10,
                                     cw3 = (60, 40, 200),
                                     adj = 3,
                                     parent = colLayoutMain
                                     )
    ### select the snow direction
    rowLayoutAngle = pm.rowLayout(nc = 6,
                                  cw6 = (110, 45, 20, 45, 20, 45),
                                  co6 = (0, 0, 0, 0, 0, 0),
                                  parent = colLayoutMain
                                  )
    pm.text(label = 'Direction Vector:       X',
            parent = rowLayoutAngle
            )

    directionX = pm.textField('DVX',
                              tx = '0.000',
                              parent = rowLayoutAngle
                              )
    pm.text(label = '   Y',
            parent = rowLayoutAngle
            )
    directionY = pm.textField('DVY',
                              tx = '-1.000',
                              parent = rowLayoutAngle
                              )    
    pm.text(label = '   Z',
            parent = rowLayoutAngle
            )
    directionZ = pm.textField('DVZ',
                              tx = '0.000',
                              parent = rowLayoutAngle
                              )    

    ### layout for cover objects options
    rowLayoutCover = pm.rowLayout(nc = 2,
                                  cw2 = (150, 150),
                                  co2 = (20, 20),
                                  parent = colLayoutMain
                                  )
    buttonCover = pm.button(label = 'Select Objects Collide With',
                            width = 150,
                            command = pm.Callback(selectObj, 2),
                            parent = rowLayoutCover
                            )
    ckboxCover = pm.checkBox(label = 'Make Collision',
                             value= True, 
                             parent = rowLayoutCover
                             )    
    
    ### layout for start generation button and cancel button
    rowLayoutButton = pm.rowLayout(nc = 2,
                                   cw2 = ((winWidth/2), (winWidth/2)),
                                   co2 = (40, 20),
                                   parent = colLayoutMain
                                   )
    buttonStart = pm.button(label = 'Start Snow!',
                            width = 100
                            )
    buttonStart.setCommand(pm.Callback(run,
                                       sliderSize = sliderSize,
                                       sliderDensity = sliderDensity,
                                       sliderHeight = sliderHeight,
                                       textSequence = textSequence,
                                       ckboxTexture = ckboxTexture,
                                       ckboxSequence = ckboxSequence,
                                       ckboxCover = ckboxCover,
                                       directionX = directionX,
                                       directionY = directionY,
                                       directionZ = directionZ,
                                       snowPieceBrowser = snowPieceBrowser
                                       )
                           )
    buttonCancel = pm.button(label = 'Cancel',
                             width = 100,
                             command = pm.Callback(snowWin.delete)
                             )
    snowWin.show()
    snowWin.setWidthHeight((winWidth, winHeight))
                            
    logger.info('UI launched')
    return
