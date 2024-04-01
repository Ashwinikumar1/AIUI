const sphereRad = 280 // 20..500
let framesPerRotation = 5000
let r, g, b  // particle color

const setLightBlue = () => {
    r = 52
    g = 235
    b = 222
}

setLightBlue()

const turnSpeed = () => 2 * Math.PI / framesPerRotation //the sphere will rotate at this speed (one complete rotation every 1600 frames).

const onUserSpeaking = () => {
    console.log("user speaking")
    framesPerRotation = 5000
}
const onProcessing = () => {
    console.log("processing")
    framesPerRotation = 1000
}
const onAiSpeaking = () => {
    console.log("ai speaking")
    framesPerRotation = 5000
}
const reset = () => {
    console.log("reset")
    framesPerRotation = 5000
    setLightBlue()
}

const wait = 1
let count = wait - 1
const fLen = 320 // represents the distance from the viewer to z=0 depth.
let m

// we will not draw coordinates if they have too large of a z-coordinate (which means they are very close to the observer).
const zMax = fLen - 2
let turnAngle = 1 //initial angle
const sphereCenterY = 0, sphereCenterZ = -3 - sphereRad

//alpha values will lessen as particles move further back, causing depth-based darkening:
const zeroAlphaDepth = -750

//random acceleration factors - causes some random motion
const randAccelX = 0.1, randAccelY = 0.1, randAccelZ = 0.1
const rgbString = () => "rgba(" + r + "," + g + "," + b + "," //partial string for color which will be completed by appending alpha value.
//we are defining a lot of variables used in the screen update functions globally so that they don't have to be redefined every frame.
let p
let outsideTest
let nextParticle
let sinAngle
let cosAngle
let rotX, rotZ
let depthAlphaFactor
let i
let theta, phi
let x0, y0, z0

function draw(context, displayWidth, displayHeight, projCenterX, projCenterY) {
    //update viewing angle
    turnAngle = (turnAngle + turnSpeed()) % (2 * Math.PI)
    sinAngle = Math.sin(turnAngle)
    cosAngle = Math.cos(turnAngle)

    //background fill
    context.fillStyle = "#000000"
    context.fillRect(0, 0, displayWidth, displayHeight)

    //update and draw waves
    for (let y = 0; y < displayHeight; y += 5) {
        let xPos = 0;
        const yOffset = y - displayHeight / 2;
        const zPos = Math.sin(yOffset / 20 + (turnAngle)) * 100;
        context.fillStyle = rgbString() + (1 - Math.abs(yOffset / displayHeight)) + ")"
        context.beginPath();
        context.moveTo(0, y);
        for (let x = 0; x < displayWidth; x += 10) {
            context.lineTo(xPos, y + zPos);
            xPos += 10;
        }
        context.lineTo(displayWidth, y);
        context.closePath();
        context.fill();
    }
}

export const particleActions = {
    onUserSpeaking,
    onProcessing,
    onAiSpeaking,
    reset,
    draw
};
