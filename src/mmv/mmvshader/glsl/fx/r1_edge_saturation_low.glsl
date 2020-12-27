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
//DESC Make the edges less saturated (towards grayscale)
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

    vec2 center = vec2(0.5, 0.5);

    vec2 polar = HOOKED_pos - center;
    // float r = pow(pow(polar.y, 2.0) + pow(polar.x, 2.0), 0.5);
    float r = pow(pow(polar.y, 2.0) + pow(polar.x, 2.0), amount);

    vec4 video = HOOKED_tex(HOOKED_pos);

    // float ratio_here = 1.0 - (r);
    float avg = (video.r + video.g + video.b) / 3.0;

    float sat = 1.4;
    video.r = ((avg - video.r) * (r)) + video.r;
    video.g = ((avg - video.g) * (r)) + video.g;
    video.b = ((avg - video.b) * (r)) + video.b;

    return video;
}

