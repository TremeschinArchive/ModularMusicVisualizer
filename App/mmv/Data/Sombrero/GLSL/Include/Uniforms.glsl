
// ===============================================================================
// // Uniforms

// Time, resolution, window
uniform int mFrame;
uniform float mTime;
uniform vec2 mMouse;
uniform vec2 mResolution;
uniform int mFlip;

// Interactive
uniform bool mIsGuiVisible;
uniform bool mIsDebugMode;

// 2D
uniform float m2DRotation;
uniform float m2DZoom;
uniform vec2 m2DDrag;
uniform bool m2DIsDraggingMode;
uniform bool m2DIsDragging;

// 3D
uniform mat3 m3DCameraBase;
uniform vec3 m3DCameraPos;
uniform vec3 m3DCameraPointing;
uniform float m3DFOV;
uniform float m3DAzimuth;
uniform float m3DInclination;
uniform float m3DRadius; 
uniform float m3DRoll;

// Keys
uniform bool mMouse1;
uniform bool mMouse2;
uniform bool mMouse3;
uniform bool mKeyCtrl;
uniform bool mKeyShift;
uniform bool mKeyAlt;

// ===============================================================================
