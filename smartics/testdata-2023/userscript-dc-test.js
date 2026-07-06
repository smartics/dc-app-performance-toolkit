/*
 * Copyright 2019-2020 Kronseder & Reiner GmbH, smartics
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

"use strict";

AJS.toInit(function () {
  const bannerWidthWithLabel = 32;
  const bannerWidthWithoutLabel = 6;

  const $main = AJS.$("#main");
  const fetchLabel = function () {
    return AJS.params.spaceName;
  }
  const fetchColors = function () {
    return ["blueviolet", "white"];
  }

  const paddingLeft = 100;
  const minWidth = 5;
  const $sidebarContainer = AJS.$("#sidebar-container");
  const $banner = AJS.$("<div id=\"userscripts-dc-test-banner\">userscripts-dc-test-banner</div>\n");
  $banner.css({
    "background-color": "#ff5511",
    "visibility": "visible",
    "z-index": "100",
    "min-width": minWidth + "px",
    "max-width": minWidth + "px",
    "min-height": "-webkit-fill-available",
    "margin-left": "0",
    "margin-top": "0",
    "position": "absolute",
    "display": "block",
    "top": "0",
    "left": "0"
  });
  $sidebarContainer.append($banner);
});
