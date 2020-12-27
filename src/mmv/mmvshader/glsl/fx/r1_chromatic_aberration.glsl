// ===============================================================================
//                                 GPL v3 License                                
// ===============================================================================
//
// Copyright (c) 2020,
//   - Tremeschin < https://tremeschin.gitlab.io > 
//
// ===============================================================================
//
// Purpose: (poor) Chromatic Aberration filter, warps a bit the space around
// the center (sadly, but it gives an interesting effect nevertheless).
//
// ===============================================================================
//
// This program is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free Software
// Foundation, either version 3 of the License, or (at your option) any later
// version.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
// You should have received a copy of the GNU General Public License along with
// this program. If not, see <http://www.gnu.org/licenses/>.
//
// ===============================================================================

// // // // // // // // // // // // // // // // // // // // // // // // // // // //
// // // // // // // // // // // // // // // // // // // // // // // // // // // //

//DESC
//DESC ------------------------------- [ DESCRIPTION ] -------------------------------
//DESC
//DESC Lens distortion, chromatic aberration 
//DESC
//DESC -------------------------------- [ VARIABLES ] --------------------------------
//DESC
//DESC >> [ Intensity ]:
//DESC
//DESC VAR <+amount_values+> array size N=frame_count (you should only send this on shader maker)
//DESC VAR <+number_of_amount_values+> int length of amount_values array
//DESC
//DESC -------------------------------------------------------------------------------
//DESC

// // // // // // // // // // // // // // // // // // // // // // // // // // // //
// // // // // // // // // // // // // // // // // // // // // // // // // // // //

//!HOOK SCALED
//!BIND HOOKED

// Standard MMV procedure for defining a constant or changing value as time goes on
const float amount_values[<+number_of_amount_values+>] = {<+changing_amount+>};

vec4 hook() {
    float amount = amount_values[frame % <+number_of_amount_values+>];
    <+activation+>;

    vec4 video = vec4(0.0);
    
    // Random values for organic FX
    float b1 = (sin(frame/30.0)/100.0) * amount;
    float b2 = (sin(frame/30.0)/50.0) * amount;
    float b3 = (sin(frame/20.0)/75.0) * amount;
    float b4 = (sin(frame/40.0)/80.0) * amount;
    float b5 = (sin(frame/45.0)/90.0) * amount;

    // float wide = (sin(frame/32.0)/256.0) - 0.05;
    float wide = 0;

    vec2 translate = vec2(sin(frame/40.0), cos(frame/50.0));
    translate /= 20;

    vec2 center_r = vec2(0.5, 0.5 + b5) + translate;
    vec2 center_g = vec2(0.5 + b4, 0.495) + translate;
    vec2 center_b = vec2(0.505, 0.5 + b3) + translate;

    // Translate
    vec2 polar_r = HOOKED_pos - center_r;
    vec2 polar_g = HOOKED_pos - center_g;
    vec2 polar_b = HOOKED_pos - center_b;

    // Get radius and angle
    float angle_r = atan(polar_r.y, polar_r.x);
    float angle_g = atan(polar_g.y, polar_g.x);
    float angle_b = atan(polar_b.y, polar_b.x);

    float r_r = pow(pow(polar_r.y, 2.0) + pow(polar_r.x, 2.0), 0.5 + wide);
    float r_g = pow(pow(polar_g.y, 2.0) + pow(polar_g.x, 2.0), 0.5 + wide);
    float r_b = pow(pow(polar_b.y, 2.0) + pow(polar_b.x, 2.0), 0.5 + wide);

    video.r = HOOKED_tex(
        vec2(
            pow(r_r, 1 + (0.06 * amount)) * cos(angle_r),
            pow(r_r, 1.0 + (0.05 * amount)) * sin(angle_r)) + center_r
    ).r;

    video.g = HOOKED_tex(
        vec2(
            pow(r_g, 1.0 + (0.03 * amount)) * cos(angle_g),
            pow(r_g, 1.0 + ((0.05 + b1) * amount)) * sin(angle_g)) + center_g
    ).g;

    video.b = HOOKED_tex(
        vec2(
            pow(r_b, 1.0 + ((0.05 + b2) * amount)) * cos(angle_b),
            pow(r_b, 1.0 + (0.04 * amount)) * sin(angle_b)) + center_b
    ).b;

    return video;
}

