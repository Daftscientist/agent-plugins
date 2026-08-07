# Office API reference

Generated from the live typed MCP registry.

## Tools

### `presentation_create` — Create presentation

Create a new editable PowerPoint presentation from semantic inline-styled HTML.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    },
    "CustomSlideSize": {
      "additionalProperties": false,
      "properties": {
        "height_in": {
          "exclusiveMinimum": 0,
          "maximum": 56.0,
          "title": "Height In",
          "type": "number"
        },
        "type": {
          "const": "custom",
          "default": "custom",
          "title": "Type",
          "type": "string"
        },
        "width_in": {
          "exclusiveMinimum": 0,
          "maximum": 56.0,
          "title": "Width In",
          "type": "number"
        }
      },
      "required": [
        "width_in",
        "height_in"
      ],
      "title": "CustomSlideSize",
      "type": "object"
    },
    "NewSlide": {
      "additionalProperties": false,
      "properties": {
        "description": {
          "anyOf": [
            {
              "maxLength": 240,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Description"
        },
        "html": {
          "minLength": 1,
          "title": "Html",
          "type": "string"
        },
        "name": {
          "maxLength": 80,
          "minLength": 1,
          "title": "Name",
          "type": "string"
        },
        "size": {
          "anyOf": [
            {
              "discriminator": {
                "mapping": {
                  "custom": "#/$defs/CustomSlideSize",
                  "preset": "#/$defs/PresetSlideSize"
                },
                "propertyName": "type"
              },
              "oneOf": [
                {
                  "$ref": "#/$defs/PresetSlideSize"
                },
                {
                  "$ref": "#/$defs/CustomSlideSize"
                }
              ]
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Size"
        },
        "transition": {
          "anyOf": [
            {
              "$ref": "#/$defs/SlideTransition"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": [
        "name",
        "html"
      ],
      "title": "NewSlide",
      "type": "object"
    },
    "PresentationTheme": {
      "additionalProperties": false,
      "properties": {
        "fonts": {
          "$ref": "#/$defs/ThemeFonts"
        },
        "palette": {
          "$ref": "#/$defs/ThemePalette"
        }
      },
      "title": "PresentationTheme",
      "type": "object"
    },
    "PresetSlideSize": {
      "additionalProperties": false,
      "properties": {
        "preset": {
          "$ref": "#/$defs/SlideSizePreset",
          "default": "16:9"
        },
        "type": {
          "const": "preset",
          "default": "preset",
          "title": "Type",
          "type": "string"
        }
      },
      "title": "PresetSlideSize",
      "type": "object"
    },
    "SlideSizePreset": {
      "enum": [
        "16:9",
        "4:3",
        "16:10"
      ],
      "title": "SlideSizePreset",
      "type": "string"
    },
    "SlideTransition": {
      "enum": [
        "none",
        "fade",
        "push",
        "wipe",
        "cover",
        "split",
        "cut",
        "zoom",
        "dissolve",
        "morph"
      ],
      "title": "SlideTransition",
      "type": "string"
    },
    "ThemeFonts": {
      "additionalProperties": false,
      "properties": {
        "body": {
          "default": "Inter",
          "title": "Body",
          "type": "string"
        },
        "heading": {
          "default": "Inter",
          "title": "Heading",
          "type": "string"
        }
      },
      "title": "ThemeFonts",
      "type": "object"
    },
    "ThemePalette": {
      "additionalProperties": false,
      "properties": {
        "accent": {
          "default": "#4f46e5",
          "title": "Accent",
          "type": "string"
        },
        "background": {
          "default": "#ffffff",
          "title": "Background",
          "type": "string"
        },
        "foreground": {
          "default": "#0b0b0c",
          "title": "Foreground",
          "type": "string"
        },
        "muted": {
          "default": "#6b7280",
          "title": "Muted",
          "type": "string"
        }
      },
      "title": "ThemePalette",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "description": {
      "anyOf": [
        {
          "maxLength": 500,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Description"
    },
    "name": {
      "maxLength": 160,
      "minLength": 1,
      "title": "Name",
      "type": "string"
    },
    "size": {
      "default": {
        "preset": "16:9",
        "type": "preset"
      },
      "discriminator": {
        "mapping": {
          "custom": "#/$defs/CustomSlideSize",
          "preset": "#/$defs/PresetSlideSize"
        },
        "propertyName": "type"
      },
      "oneOf": [
        {
          "$ref": "#/$defs/PresetSlideSize"
        },
        {
          "$ref": "#/$defs/CustomSlideSize"
        }
      ],
      "title": "Size"
    },
    "slides": {
      "default": [],
      "items": {
        "$ref": "#/$defs/NewSlide"
      },
      "maxItems": 100,
      "title": "Slides",
      "type": "array"
    },
    "theme": {
      "$ref": "#/$defs/PresentationTheme",
      "default": {
        "fonts": {
          "body": "Inter",
          "heading": "Inter"
        },
        "palette": {
          "accent": "#4f46e5",
          "background": "#ffffff",
          "foreground": "#0b0b0c",
          "muted": "#6b7280"
        }
      }
    }
  },
  "required": [
    "name"
  ],
  "title": "presentation_createArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "$defs": {
    "SlideRef": {
      "additionalProperties": false,
      "properties": {
        "description": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Description"
        },
        "name": {
          "title": "Name",
          "type": "string"
        },
        "number": {
          "minimum": 1,
          "title": "Number",
          "type": "integer"
        },
        "slide_id": {
          "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
          "title": "Slide Id",
          "type": "string"
        }
      },
      "required": [
        "slide_id",
        "number",
        "name"
      ],
      "title": "SlideRef",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "resource_uri": {
      "title": "Resource Uri",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "slide_count": {
      "minimum": 0,
      "title": "Slide Count",
      "type": "integer"
    },
    "slides": {
      "items": {
        "$ref": "#/$defs/SlideRef"
      },
      "title": "Slides",
      "type": "array"
    }
  },
  "required": [
    "presentation_id",
    "revision",
    "name",
    "slide_count",
    "slides",
    "resource_uri"
  ],
  "title": "PresentationCreateResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": false,
  "idempotentHint": false,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

### `presentation_open` — Open presentation

Import a PPTX source into an editable workspace while preserving and reporting unsupported constructs.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    },
    "PresentationSource": {
      "additionalProperties": false,
      "properties": {
        "filename_hint": {
          "anyOf": [
            {
              "maxLength": 255,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Filename Hint"
        },
        "uri": {
          "minLength": 1,
          "title": "Uri",
          "type": "string"
        }
      },
      "required": [
        "uri"
      ],
      "title": "PresentationSource",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "description": {
      "anyOf": [
        {
          "maxLength": 500,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Description"
    },
    "name": {
      "anyOf": [
        {
          "maxLength": 160,
          "minLength": 1,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Name"
    },
    "source": {
      "$ref": "#/$defs/PresentationSource"
    }
  },
  "required": [
    "source"
  ],
  "title": "presentation_openArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "$defs": {
    "ImportWarning": {
      "additionalProperties": false,
      "properties": {
        "code": {
          "title": "Code",
          "type": "string"
        },
        "element": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Element"
        },
        "message": {
          "title": "Message",
          "type": "string"
        },
        "slide_number": {
          "anyOf": [
            {
              "minimum": 1,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Slide Number"
        }
      },
      "required": [
        "code",
        "message"
      ],
      "title": "ImportWarning",
      "type": "object"
    },
    "SlideRef": {
      "additionalProperties": false,
      "properties": {
        "description": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Description"
        },
        "name": {
          "title": "Name",
          "type": "string"
        },
        "number": {
          "minimum": 1,
          "title": "Number",
          "type": "integer"
        },
        "slide_id": {
          "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
          "title": "Slide Id",
          "type": "string"
        }
      },
      "required": [
        "slide_id",
        "number",
        "name"
      ],
      "title": "SlideRef",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "resource_uri": {
      "title": "Resource Uri",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "slide_count": {
      "minimum": 0,
      "title": "Slide Count",
      "type": "integer"
    },
    "slides": {
      "items": {
        "$ref": "#/$defs/SlideRef"
      },
      "title": "Slides",
      "type": "array"
    },
    "warnings": {
      "items": {
        "$ref": "#/$defs/ImportWarning"
      },
      "title": "Warnings",
      "type": "array"
    }
  },
  "required": [
    "presentation_id",
    "revision",
    "name",
    "slide_count",
    "slides",
    "resource_uri",
    "warnings"
  ],
  "title": "PresentationOpenResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": false,
  "idempotentHint": false,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

### `presentation_search` — Search presentations

Search persistent presentations semantically by metadata and visible slide text.

Input schema:

```json
{
  "$defs": {
    "PresentationSearchField": {
      "enum": [
        "name",
        "description",
        "slide_names",
        "slide_descriptions",
        "slide_text"
      ],
      "title": "PresentationSearchField",
      "type": "string"
    },
    "PresentationSearchSort": {
      "enum": [
        "relevance",
        "updated_desc",
        "updated_asc",
        "created_desc",
        "created_asc",
        "name_asc",
        "name_desc"
      ],
      "title": "PresentationSearchSort",
      "type": "string"
    }
  },
  "additionalProperties": false,
  "properties": {
    "created_after": {
      "anyOf": [
        {
          "format": "date-time",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Created After"
    },
    "created_before": {
      "anyOf": [
        {
          "format": "date-time",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Created Before"
    },
    "cursor": {
      "anyOf": [
        {
          "maxLength": 2048,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Cursor"
    },
    "limit": {
      "default": 20,
      "maximum": 100,
      "minimum": 1,
      "title": "Limit",
      "type": "integer"
    },
    "query": {
      "anyOf": [
        {
          "maxLength": 500,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Query"
    },
    "search_in": {
      "default": [
        "name",
        "description",
        "slide_names",
        "slide_text"
      ],
      "items": {
        "$ref": "#/$defs/PresentationSearchField"
      },
      "minItems": 1,
      "title": "Search In",
      "type": "array"
    },
    "sort": {
      "$ref": "#/$defs/PresentationSearchSort",
      "default": "relevance"
    },
    "updated_after": {
      "anyOf": [
        {
          "format": "date-time",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Updated After"
    },
    "updated_before": {
      "anyOf": [
        {
          "format": "date-time",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Updated Before"
    }
  },
  "title": "presentation_searchArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "$defs": {
    "PresentationSearchItem": {
      "additionalProperties": false,
      "properties": {
        "created_at": {
          "format": "date-time",
          "title": "Created At",
          "type": "string"
        },
        "description": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Description"
        },
        "matches": {
          "items": {
            "$ref": "#/$defs/PresentationSearchMatch"
          },
          "title": "Matches",
          "type": "array"
        },
        "name": {
          "title": "Name",
          "type": "string"
        },
        "presentation_id": {
          "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
          "title": "Presentation Id",
          "type": "string"
        },
        "resource_uri": {
          "title": "Resource Uri",
          "type": "string"
        },
        "revision": {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "title": "Revision",
          "type": "string"
        },
        "slide_count": {
          "title": "Slide Count",
          "type": "integer"
        },
        "updated_at": {
          "format": "date-time",
          "title": "Updated At",
          "type": "string"
        }
      },
      "required": [
        "presentation_id",
        "revision",
        "name",
        "description",
        "created_at",
        "updated_at",
        "slide_count",
        "matches",
        "resource_uri"
      ],
      "title": "PresentationSearchItem",
      "type": "object"
    },
    "PresentationSearchMatch": {
      "additionalProperties": false,
      "properties": {
        "slide_id": {
          "anyOf": [
            {
              "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Slide Id"
        },
        "slide_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Slide Name"
        },
        "snippet": {
          "title": "Snippet",
          "type": "string"
        }
      },
      "required": [
        "snippet"
      ],
      "title": "PresentationSearchMatch",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "items": {
      "items": {
        "$ref": "#/$defs/PresentationSearchItem"
      },
      "title": "Items",
      "type": "array"
    },
    "next_cursor": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Next Cursor"
    }
  },
  "required": [
    "items"
  ],
  "title": "PresentationSearchResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": null,
  "idempotentHint": null,
  "openWorldHint": false,
  "readOnlyHint": true,
  "title": null
}
```

### `presentation_inspect` — Inspect presentation

Inspect presentation metadata and outline without loading slide HTML. Use this first for an existing deck.

Input schema:

```json
{
  "$defs": {
    "PresentationInspectDetail": {
      "enum": [
        "summary",
        "outline"
      ],
      "title": "PresentationInspectDetail",
      "type": "string"
    }
  },
  "additionalProperties": false,
  "properties": {
    "detail": {
      "$ref": "#/$defs/PresentationInspectDetail",
      "default": "outline"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Revision"
    }
  },
  "required": [
    "presentation_id"
  ],
  "title": "presentation_inspectArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "$defs": {
    "CustomSlideSize": {
      "additionalProperties": false,
      "properties": {
        "height_in": {
          "exclusiveMinimum": 0,
          "maximum": 56.0,
          "title": "Height In",
          "type": "number"
        },
        "type": {
          "const": "custom",
          "default": "custom",
          "title": "Type",
          "type": "string"
        },
        "width_in": {
          "exclusiveMinimum": 0,
          "maximum": 56.0,
          "title": "Width In",
          "type": "number"
        }
      },
      "required": [
        "width_in",
        "height_in"
      ],
      "title": "CustomSlideSize",
      "type": "object"
    },
    "PresentationTheme": {
      "additionalProperties": false,
      "properties": {
        "fonts": {
          "$ref": "#/$defs/ThemeFonts"
        },
        "palette": {
          "$ref": "#/$defs/ThemePalette"
        }
      },
      "title": "PresentationTheme",
      "type": "object"
    },
    "PresetSlideSize": {
      "additionalProperties": false,
      "properties": {
        "preset": {
          "$ref": "#/$defs/SlideSizePreset",
          "default": "16:9"
        },
        "type": {
          "const": "preset",
          "default": "preset",
          "title": "Type",
          "type": "string"
        }
      },
      "title": "PresetSlideSize",
      "type": "object"
    },
    "SlideRef": {
      "additionalProperties": false,
      "properties": {
        "description": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Description"
        },
        "name": {
          "title": "Name",
          "type": "string"
        },
        "number": {
          "minimum": 1,
          "title": "Number",
          "type": "integer"
        },
        "slide_id": {
          "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
          "title": "Slide Id",
          "type": "string"
        }
      },
      "required": [
        "slide_id",
        "number",
        "name"
      ],
      "title": "SlideRef",
      "type": "object"
    },
    "SlideSizePreset": {
      "enum": [
        "16:9",
        "4:3",
        "16:10"
      ],
      "title": "SlideSizePreset",
      "type": "string"
    },
    "ThemeFonts": {
      "additionalProperties": false,
      "properties": {
        "body": {
          "default": "Inter",
          "title": "Body",
          "type": "string"
        },
        "heading": {
          "default": "Inter",
          "title": "Heading",
          "type": "string"
        }
      },
      "title": "ThemeFonts",
      "type": "object"
    },
    "ThemePalette": {
      "additionalProperties": false,
      "properties": {
        "accent": {
          "default": "#4f46e5",
          "title": "Accent",
          "type": "string"
        },
        "background": {
          "default": "#ffffff",
          "title": "Background",
          "type": "string"
        },
        "foreground": {
          "default": "#0b0b0c",
          "title": "Foreground",
          "type": "string"
        },
        "muted": {
          "default": "#6b7280",
          "title": "Muted",
          "type": "string"
        }
      },
      "title": "ThemePalette",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "created_at": {
      "format": "date-time",
      "title": "Created At",
      "type": "string"
    },
    "description": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "title": "Description"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "size": {
      "discriminator": {
        "mapping": {
          "custom": "#/$defs/CustomSlideSize",
          "preset": "#/$defs/PresetSlideSize"
        },
        "propertyName": "type"
      },
      "oneOf": [
        {
          "$ref": "#/$defs/PresetSlideSize"
        },
        {
          "$ref": "#/$defs/CustomSlideSize"
        }
      ],
      "title": "Size"
    },
    "slide_count": {
      "title": "Slide Count",
      "type": "integer"
    },
    "slides": {
      "items": {
        "$ref": "#/$defs/SlideRef"
      },
      "title": "Slides",
      "type": "array"
    },
    "theme": {
      "$ref": "#/$defs/PresentationTheme"
    },
    "updated_at": {
      "format": "date-time",
      "title": "Updated At",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "revision",
    "name",
    "description",
    "size",
    "theme",
    "created_at",
    "updated_at",
    "slide_count",
    "slides"
  ],
  "title": "PresentationInspectResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": null,
  "idempotentHint": null,
  "openWorldHint": false,
  "readOnlyHint": true,
  "title": null
}
```

### `presentation_update` — Update presentation

Update presentation metadata, size, or theme as one optimistic revision.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    },
    "CustomSlideSize": {
      "additionalProperties": false,
      "properties": {
        "height_in": {
          "exclusiveMinimum": 0,
          "maximum": 56.0,
          "title": "Height In",
          "type": "number"
        },
        "type": {
          "const": "custom",
          "default": "custom",
          "title": "Type",
          "type": "string"
        },
        "width_in": {
          "exclusiveMinimum": 0,
          "maximum": 56.0,
          "title": "Width In",
          "type": "number"
        }
      },
      "required": [
        "width_in",
        "height_in"
      ],
      "title": "CustomSlideSize",
      "type": "object"
    },
    "PresentationThemePatch": {
      "additionalProperties": false,
      "properties": {
        "fonts": {
          "anyOf": [
            {
              "$ref": "#/$defs/ThemeFontsPatch"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "palette": {
          "anyOf": [
            {
              "$ref": "#/$defs/ThemePalettePatch"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "title": "PresentationThemePatch",
      "type": "object"
    },
    "PresetSlideSize": {
      "additionalProperties": false,
      "properties": {
        "preset": {
          "$ref": "#/$defs/SlideSizePreset",
          "default": "16:9"
        },
        "type": {
          "const": "preset",
          "default": "preset",
          "title": "Type",
          "type": "string"
        }
      },
      "title": "PresetSlideSize",
      "type": "object"
    },
    "SlideSizePreset": {
      "enum": [
        "16:9",
        "4:3",
        "16:10"
      ],
      "title": "SlideSizePreset",
      "type": "string"
    },
    "ThemeFontsPatch": {
      "additionalProperties": false,
      "properties": {
        "body": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Body"
        },
        "heading": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Heading"
        }
      },
      "title": "ThemeFontsPatch",
      "type": "object"
    },
    "ThemePalettePatch": {
      "additionalProperties": false,
      "properties": {
        "accent": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Accent"
        },
        "background": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Background"
        },
        "foreground": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Foreground"
        },
        "muted": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Muted"
        }
      },
      "title": "ThemePalettePatch",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "description": {
      "anyOf": [
        {
          "maxLength": 500,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Description"
    },
    "expected_revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Revision"
    },
    "name": {
      "anyOf": [
        {
          "maxLength": 160,
          "minLength": 1,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Name"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "size": {
      "anyOf": [
        {
          "discriminator": {
            "mapping": {
              "custom": "#/$defs/CustomSlideSize",
              "preset": "#/$defs/PresetSlideSize"
            },
            "propertyName": "type"
          },
          "oneOf": [
            {
              "$ref": "#/$defs/PresetSlideSize"
            },
            {
              "$ref": "#/$defs/CustomSlideSize"
            }
          ]
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Size"
    },
    "theme": {
      "anyOf": [
        {
          "$ref": "#/$defs/PresentationThemePatch"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    }
  },
  "required": [
    "presentation_id"
  ],
  "title": "presentation_updateArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "additionalProperties": false,
  "properties": {
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "previous_revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Previous Revision",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "previous_revision",
    "revision"
  ],
  "title": "MutationResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": false,
  "idempotentHint": false,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

### `presentation_validate` — Validate presentation

Validate domOXML representation, editability, source-retention coverage, warnings, and failures.

Input schema:

```json
{
  "$defs": {
    "ValidationDetail": {
      "enum": [
        "summary",
        "full"
      ],
      "title": "ValidationDetail",
      "type": "string"
    }
  },
  "additionalProperties": false,
  "properties": {
    "detail": {
      "$ref": "#/$defs/ValidationDetail",
      "default": "summary"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Revision"
    },
    "slide_ids": {
      "anyOf": [
        {
          "items": {
            "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Slide Ids"
    }
  },
  "required": [
    "presentation_id"
  ],
  "title": "presentation_validateArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "$defs": {
    "CoverageItem": {
      "additionalProperties": false,
      "properties": {
        "editability": {
          "$ref": "#/$defs/Editability"
        },
        "element": {
          "title": "Element",
          "type": "string"
        },
        "output_count": {
          "minimum": 0,
          "title": "Output Count",
          "type": "integer"
        },
        "raster_area_emu2": {
          "minimum": 0,
          "title": "Raster Area Emu2",
          "type": "integer"
        },
        "reason": {
          "title": "Reason",
          "type": "string"
        },
        "representation": {
          "$ref": "#/$defs/Representation"
        },
        "slide_id": {
          "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
          "title": "Slide Id",
          "type": "string"
        },
        "source_retention": {
          "$ref": "#/$defs/SourceRetention"
        }
      },
      "required": [
        "slide_id",
        "element",
        "representation",
        "editability",
        "source_retention",
        "output_count",
        "raster_area_emu2",
        "reason"
      ],
      "title": "CoverageItem",
      "type": "object"
    },
    "Editability": {
      "enum": [
        "semantic",
        "components",
        "layers",
        "none"
      ],
      "title": "Editability",
      "type": "string"
    },
    "Representation": {
      "enum": [
        "native",
        "decomposed",
        "hybrid",
        "layered",
        "element_layer",
        "rasterized",
        "approximated",
        "failed"
      ],
      "title": "Representation",
      "type": "string"
    },
    "SourceRetention": {
      "enum": [
        "not_required",
        "attached",
        "detached",
        "ignored",
        "lost"
      ],
      "title": "SourceRetention",
      "type": "string"
    },
    "ValidationWarning": {
      "additionalProperties": false,
      "properties": {
        "code": {
          "title": "Code",
          "type": "string"
        },
        "element": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Element"
        },
        "message": {
          "title": "Message",
          "type": "string"
        },
        "slide_id": {
          "anyOf": [
            {
              "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Slide Id"
        }
      },
      "required": [
        "code",
        "message"
      ],
      "title": "ValidationWarning",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "coverage": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/CoverageItem"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Coverage"
    },
    "editable_ratio": {
      "maximum": 1,
      "minimum": 0,
      "title": "Editable Ratio",
      "type": "number"
    },
    "failed_count": {
      "minimum": 0,
      "title": "Failed Count",
      "type": "integer"
    },
    "layered_ratio": {
      "maximum": 1,
      "minimum": 0,
      "title": "Layered Ratio",
      "type": "number"
    },
    "native_ratio": {
      "maximum": 1,
      "minimum": 0,
      "title": "Native Ratio",
      "type": "number"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "slide_count": {
      "title": "Slide Count",
      "type": "integer"
    },
    "valid": {
      "title": "Valid",
      "type": "boolean"
    },
    "warning_count": {
      "minimum": 0,
      "title": "Warning Count",
      "type": "integer"
    },
    "warnings": {
      "items": {
        "$ref": "#/$defs/ValidationWarning"
      },
      "title": "Warnings",
      "type": "array"
    }
  },
  "required": [
    "presentation_id",
    "revision",
    "valid",
    "slide_count",
    "native_ratio",
    "editable_ratio",
    "layered_ratio",
    "warning_count",
    "failed_count",
    "warnings"
  ],
  "title": "PresentationValidationResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": null,
  "idempotentHint": null,
  "openWorldHint": false,
  "readOnlyHint": true,
  "title": null
}
```

### `presentation_preview` — Preview presentation

Render selected slides. One slide returns detail; multiple slides return bounded contact sheets.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    },
    "PreviewAll": {
      "additionalProperties": false,
      "properties": {
        "type": {
          "const": "all",
          "default": "all",
          "title": "Type",
          "type": "string"
        }
      },
      "title": "PreviewAll",
      "type": "object"
    },
    "PreviewLabels": {
      "enum": [
        "none",
        "number",
        "name",
        "number_and_name"
      ],
      "title": "PreviewLabels",
      "type": "string"
    },
    "PreviewLayout": {
      "enum": [
        "auto",
        "single",
        "contact_sheet"
      ],
      "title": "PreviewLayout",
      "type": "string"
    },
    "PreviewQuality": {
      "enum": [
        "standard",
        "high"
      ],
      "title": "PreviewQuality",
      "type": "string"
    },
    "PreviewRange": {
      "additionalProperties": false,
      "properties": {
        "end": {
          "minimum": 1,
          "title": "End",
          "type": "integer"
        },
        "start": {
          "minimum": 1,
          "title": "Start",
          "type": "integer"
        },
        "type": {
          "const": "range",
          "default": "range",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "start",
        "end"
      ],
      "title": "PreviewRange",
      "type": "object"
    },
    "PreviewSlides": {
      "additionalProperties": false,
      "properties": {
        "slide_ids": {
          "items": {
            "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
            "type": "string"
          },
          "maxItems": 100,
          "minItems": 1,
          "title": "Slide Ids",
          "type": "array"
        },
        "type": {
          "const": "slides",
          "default": "slides",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "slide_ids"
      ],
      "title": "PreviewSlides",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "columns": {
      "anyOf": [
        {
          "enum": [
            2,
            3,
            4,
            5
          ],
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Columns"
    },
    "labels": {
      "$ref": "#/$defs/PreviewLabels",
      "default": "number_and_name"
    },
    "layout": {
      "$ref": "#/$defs/PreviewLayout",
      "default": "auto"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "quality": {
      "$ref": "#/$defs/PreviewQuality",
      "default": "standard"
    },
    "revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Revision"
    },
    "selection": {
      "default": {
        "type": "all"
      },
      "discriminator": {
        "mapping": {
          "all": "#/$defs/PreviewAll",
          "range": "#/$defs/PreviewRange",
          "slides": "#/$defs/PreviewSlides"
        },
        "propertyName": "type"
      },
      "oneOf": [
        {
          "$ref": "#/$defs/PreviewAll"
        },
        {
          "$ref": "#/$defs/PreviewRange"
        },
        {
          "$ref": "#/$defs/PreviewSlides"
        }
      ],
      "title": "Selection"
    }
  },
  "required": [
    "presentation_id"
  ],
  "title": "presentation_previewArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "$defs": {
    "PreviewImageDescriptor": {
      "additionalProperties": false,
      "properties": {
        "height_px": {
          "exclusiveMinimum": 0,
          "title": "Height Px",
          "type": "integer"
        },
        "mime_type": {
          "const": "image/png",
          "default": "image/png",
          "title": "Mime Type",
          "type": "string"
        },
        "page": {
          "minimum": 1,
          "title": "Page",
          "type": "integer"
        },
        "slide_ids": {
          "items": {
            "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
            "type": "string"
          },
          "title": "Slide Ids",
          "type": "array"
        },
        "width_px": {
          "exclusiveMinimum": 0,
          "title": "Width Px",
          "type": "integer"
        }
      },
      "required": [
        "page",
        "slide_ids",
        "width_px",
        "height_px"
      ],
      "title": "PreviewImageDescriptor",
      "type": "object"
    },
    "PreviewLayout": {
      "enum": [
        "auto",
        "single",
        "contact_sheet"
      ],
      "title": "PreviewLayout",
      "type": "string"
    }
  },
  "additionalProperties": false,
  "properties": {
    "images": {
      "items": {
        "$ref": "#/$defs/PreviewImageDescriptor"
      },
      "title": "Images",
      "type": "array"
    },
    "layout": {
      "$ref": "#/$defs/PreviewLayout"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "revision",
    "layout",
    "images"
  ],
  "title": "PresentationPreviewResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": null,
  "idempotentHint": null,
  "openWorldHint": false,
  "readOnlyHint": true,
  "title": null
}
```

### `presentation_export` — Export presentation

Materialise an immutable PPTX for a specific revision and return its resource link.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "filename": {
      "anyOf": [
        {
          "maxLength": 255,
          "minLength": 1,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Filename"
    },
    "format": {
      "const": "pptx",
      "default": "pptx",
      "title": "Format",
      "type": "string"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Revision"
    }
  },
  "required": [
    "presentation_id"
  ],
  "title": "presentation_exportArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "additionalProperties": false,
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "mime_type": {
      "const": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      "title": "Mime Type",
      "type": "string"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "resource_uri": {
      "title": "Resource Uri",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "sha256": {
      "pattern": "^[0-9a-f]{64}$",
      "title": "Sha256",
      "type": "string"
    },
    "size_bytes": {
      "minimum": 0,
      "title": "Size Bytes",
      "type": "integer"
    }
  },
  "required": [
    "presentation_id",
    "revision",
    "filename",
    "mime_type",
    "size_bytes",
    "sha256",
    "resource_uri"
  ],
  "title": "PresentationExportResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": null,
  "idempotentHint": null,
  "openWorldHint": false,
  "readOnlyHint": true,
  "title": null
}
```

### `presentation_delete` — Delete presentation

Permanently delete a standalone Office presentation and all stored revisions.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "expected_revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Revision"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    }
  },
  "required": [
    "presentation_id"
  ],
  "title": "presentation_deleteArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "additionalProperties": false,
  "properties": {
    "deleted": {
      "const": true,
      "default": true,
      "title": "Deleted",
      "type": "boolean"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    }
  },
  "required": [
    "presentation_id"
  ],
  "title": "PresentationDeleteResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": true,
  "idempotentHint": true,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

### `slide_add` — Add slides

Add one or more named inline-HTML slides in one transaction and revision.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    },
    "CustomSlideSize": {
      "additionalProperties": false,
      "properties": {
        "height_in": {
          "exclusiveMinimum": 0,
          "maximum": 56.0,
          "title": "Height In",
          "type": "number"
        },
        "type": {
          "const": "custom",
          "default": "custom",
          "title": "Type",
          "type": "string"
        },
        "width_in": {
          "exclusiveMinimum": 0,
          "maximum": 56.0,
          "title": "Width In",
          "type": "number"
        }
      },
      "required": [
        "width_in",
        "height_in"
      ],
      "title": "CustomSlideSize",
      "type": "object"
    },
    "InsertAfter": {
      "additionalProperties": false,
      "properties": {
        "slide_id": {
          "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
          "title": "Slide Id",
          "type": "string"
        },
        "type": {
          "const": "after",
          "default": "after",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "slide_id"
      ],
      "title": "InsertAfter",
      "type": "object"
    },
    "InsertBefore": {
      "additionalProperties": false,
      "properties": {
        "slide_id": {
          "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
          "title": "Slide Id",
          "type": "string"
        },
        "type": {
          "const": "before",
          "default": "before",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "slide_id"
      ],
      "title": "InsertBefore",
      "type": "object"
    },
    "InsertEnd": {
      "additionalProperties": false,
      "properties": {
        "type": {
          "const": "end",
          "default": "end",
          "title": "Type",
          "type": "string"
        }
      },
      "title": "InsertEnd",
      "type": "object"
    },
    "InsertStart": {
      "additionalProperties": false,
      "properties": {
        "type": {
          "const": "start",
          "default": "start",
          "title": "Type",
          "type": "string"
        }
      },
      "title": "InsertStart",
      "type": "object"
    },
    "NewSlide": {
      "additionalProperties": false,
      "properties": {
        "description": {
          "anyOf": [
            {
              "maxLength": 240,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Description"
        },
        "html": {
          "minLength": 1,
          "title": "Html",
          "type": "string"
        },
        "name": {
          "maxLength": 80,
          "minLength": 1,
          "title": "Name",
          "type": "string"
        },
        "size": {
          "anyOf": [
            {
              "discriminator": {
                "mapping": {
                  "custom": "#/$defs/CustomSlideSize",
                  "preset": "#/$defs/PresetSlideSize"
                },
                "propertyName": "type"
              },
              "oneOf": [
                {
                  "$ref": "#/$defs/PresetSlideSize"
                },
                {
                  "$ref": "#/$defs/CustomSlideSize"
                }
              ]
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Size"
        },
        "transition": {
          "anyOf": [
            {
              "$ref": "#/$defs/SlideTransition"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": [
        "name",
        "html"
      ],
      "title": "NewSlide",
      "type": "object"
    },
    "PresetSlideSize": {
      "additionalProperties": false,
      "properties": {
        "preset": {
          "$ref": "#/$defs/SlideSizePreset",
          "default": "16:9"
        },
        "type": {
          "const": "preset",
          "default": "preset",
          "title": "Type",
          "type": "string"
        }
      },
      "title": "PresetSlideSize",
      "type": "object"
    },
    "SlideSizePreset": {
      "enum": [
        "16:9",
        "4:3",
        "16:10"
      ],
      "title": "SlideSizePreset",
      "type": "string"
    },
    "SlideTransition": {
      "enum": [
        "none",
        "fade",
        "push",
        "wipe",
        "cover",
        "split",
        "cut",
        "zoom",
        "dissolve",
        "morph"
      ],
      "title": "SlideTransition",
      "type": "string"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "expected_revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Revision"
    },
    "position": {
      "default": {
        "type": "end"
      },
      "discriminator": {
        "mapping": {
          "after": "#/$defs/InsertAfter",
          "before": "#/$defs/InsertBefore",
          "end": "#/$defs/InsertEnd",
          "start": "#/$defs/InsertStart"
        },
        "propertyName": "type"
      },
      "oneOf": [
        {
          "$ref": "#/$defs/InsertStart"
        },
        {
          "$ref": "#/$defs/InsertEnd"
        },
        {
          "$ref": "#/$defs/InsertBefore"
        },
        {
          "$ref": "#/$defs/InsertAfter"
        }
      ],
      "title": "Position"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "slides": {
      "items": {
        "$ref": "#/$defs/NewSlide"
      },
      "maxItems": 50,
      "minItems": 1,
      "title": "Slides",
      "type": "array"
    }
  },
  "required": [
    "presentation_id",
    "slides"
  ],
  "title": "slide_addArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "$defs": {
    "SlideRef": {
      "additionalProperties": false,
      "properties": {
        "description": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Description"
        },
        "name": {
          "title": "Name",
          "type": "string"
        },
        "number": {
          "minimum": 1,
          "title": "Number",
          "type": "integer"
        },
        "slide_id": {
          "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
          "title": "Slide Id",
          "type": "string"
        }
      },
      "required": [
        "slide_id",
        "number",
        "name"
      ],
      "title": "SlideRef",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "added": {
      "items": {
        "$ref": "#/$defs/SlideRef"
      },
      "title": "Added",
      "type": "array"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "previous_revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Previous Revision",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "slide_count": {
      "title": "Slide Count",
      "type": "integer"
    }
  },
  "required": [
    "presentation_id",
    "previous_revision",
    "revision",
    "added",
    "slide_count"
  ],
  "title": "SlideAddResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": false,
  "idempotentHint": false,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

### `slide_inspect` — Inspect slide

Inspect one slide. Prefer structure; request source only for exact styles or redesign.

Input schema:

```json
{
  "$defs": {
    "SlideInspectDetail": {
      "enum": [
        "summary",
        "structure",
        "source"
      ],
      "title": "SlideInspectDetail",
      "type": "string"
    }
  },
  "additionalProperties": false,
  "properties": {
    "detail": {
      "$ref": "#/$defs/SlideInspectDetail",
      "default": "structure"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Revision"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "slide_id"
  ],
  "title": "slide_inspectArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "$defs": {
    "CustomSlideSize": {
      "additionalProperties": false,
      "properties": {
        "height_in": {
          "exclusiveMinimum": 0,
          "maximum": 56.0,
          "title": "Height In",
          "type": "number"
        },
        "type": {
          "const": "custom",
          "default": "custom",
          "title": "Type",
          "type": "string"
        },
        "width_in": {
          "exclusiveMinimum": 0,
          "maximum": 56.0,
          "title": "Width In",
          "type": "number"
        }
      },
      "required": [
        "width_in",
        "height_in"
      ],
      "title": "CustomSlideSize",
      "type": "object"
    },
    "ElementStructureNode": {
      "additionalProperties": false,
      "properties": {
        "child_ids": {
          "items": {
            "pattern": "^el_[A-Za-z0-9_-]{8,}$",
            "type": "string"
          },
          "title": "Child Ids",
          "type": "array"
        },
        "element_id": {
          "pattern": "^el_[A-Za-z0-9_-]{8,}$",
          "title": "Element Id",
          "type": "string"
        },
        "element_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Element Name"
        },
        "tag": {
          "title": "Tag",
          "type": "string"
        },
        "text": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Text"
        }
      },
      "required": [
        "element_id",
        "element_name",
        "tag",
        "text",
        "child_ids"
      ],
      "title": "ElementStructureNode",
      "type": "object"
    },
    "PresetSlideSize": {
      "additionalProperties": false,
      "properties": {
        "preset": {
          "$ref": "#/$defs/SlideSizePreset",
          "default": "16:9"
        },
        "type": {
          "const": "preset",
          "default": "preset",
          "title": "Type",
          "type": "string"
        }
      },
      "title": "PresetSlideSize",
      "type": "object"
    },
    "SlideSizePreset": {
      "enum": [
        "16:9",
        "4:3",
        "16:10"
      ],
      "title": "SlideSizePreset",
      "type": "string"
    },
    "SlideSummary": {
      "additionalProperties": false,
      "properties": {
        "description": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Description"
        },
        "element_count": {
          "title": "Element Count",
          "type": "integer"
        },
        "name": {
          "title": "Name",
          "type": "string"
        },
        "number": {
          "title": "Number",
          "type": "integer"
        },
        "size": {
          "anyOf": [
            {
              "discriminator": {
                "mapping": {
                  "custom": "#/$defs/CustomSlideSize",
                  "preset": "#/$defs/PresetSlideSize"
                },
                "propertyName": "type"
              },
              "oneOf": [
                {
                  "$ref": "#/$defs/PresetSlideSize"
                },
                {
                  "$ref": "#/$defs/CustomSlideSize"
                }
              ]
            },
            {
              "type": "null"
            }
          ],
          "title": "Size"
        },
        "slide_id": {
          "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
          "title": "Slide Id",
          "type": "string"
        },
        "transition": {
          "anyOf": [
            {
              "$ref": "#/$defs/SlideTransition"
            },
            {
              "type": "null"
            }
          ]
        }
      },
      "required": [
        "slide_id",
        "number",
        "name",
        "description",
        "transition",
        "size",
        "element_count"
      ],
      "title": "SlideSummary",
      "type": "object"
    },
    "SlideTransition": {
      "enum": [
        "none",
        "fade",
        "push",
        "wipe",
        "cover",
        "split",
        "cut",
        "zoom",
        "dissolve",
        "morph"
      ],
      "title": "SlideTransition",
      "type": "string"
    }
  },
  "additionalProperties": false,
  "properties": {
    "html": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Html"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "structure": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/ElementStructureNode"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Structure"
    },
    "summary": {
      "$ref": "#/$defs/SlideSummary"
    }
  },
  "required": [
    "presentation_id",
    "revision",
    "summary"
  ],
  "title": "SlideInspectResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": null,
  "idempotentHint": null,
  "openWorldHint": false,
  "readOnlyHint": true,
  "title": null
}
```

### `slide_update` — Update slide

Update slide metadata or replace full HTML for a genuine redesign; prefer element_update for small edits.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    },
    "CustomSlideSize": {
      "additionalProperties": false,
      "properties": {
        "height_in": {
          "exclusiveMinimum": 0,
          "maximum": 56.0,
          "title": "Height In",
          "type": "number"
        },
        "type": {
          "const": "custom",
          "default": "custom",
          "title": "Type",
          "type": "string"
        },
        "width_in": {
          "exclusiveMinimum": 0,
          "maximum": 56.0,
          "title": "Width In",
          "type": "number"
        }
      },
      "required": [
        "width_in",
        "height_in"
      ],
      "title": "CustomSlideSize",
      "type": "object"
    },
    "PresetSlideSize": {
      "additionalProperties": false,
      "properties": {
        "preset": {
          "$ref": "#/$defs/SlideSizePreset",
          "default": "16:9"
        },
        "type": {
          "const": "preset",
          "default": "preset",
          "title": "Type",
          "type": "string"
        }
      },
      "title": "PresetSlideSize",
      "type": "object"
    },
    "SlideSizePreset": {
      "enum": [
        "16:9",
        "4:3",
        "16:10"
      ],
      "title": "SlideSizePreset",
      "type": "string"
    },
    "SlideTransition": {
      "enum": [
        "none",
        "fade",
        "push",
        "wipe",
        "cover",
        "split",
        "cut",
        "zoom",
        "dissolve",
        "morph"
      ],
      "title": "SlideTransition",
      "type": "string"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "description": {
      "anyOf": [
        {
          "maxLength": 240,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Description"
    },
    "expected_revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Revision"
    },
    "html": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Html"
    },
    "name": {
      "anyOf": [
        {
          "maxLength": 80,
          "minLength": 1,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Name"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "size": {
      "anyOf": [
        {
          "discriminator": {
            "mapping": {
              "custom": "#/$defs/CustomSlideSize",
              "preset": "#/$defs/PresetSlideSize"
            },
            "propertyName": "type"
          },
          "oneOf": [
            {
              "$ref": "#/$defs/PresetSlideSize"
            },
            {
              "$ref": "#/$defs/CustomSlideSize"
            }
          ]
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Size"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    },
    "transition": {
      "anyOf": [
        {
          "$ref": "#/$defs/SlideTransition"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    }
  },
  "required": [
    "presentation_id",
    "slide_id"
  ],
  "title": "slide_updateArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "additionalProperties": false,
  "properties": {
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "previous_revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Previous Revision",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "previous_revision",
    "revision"
  ],
  "title": "MutationResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": false,
  "idempotentHint": false,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

### `slide_duplicate` — Duplicate slide

Duplicate a slide with fresh slide and element IDs for layout reuse.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    },
    "InsertAfter": {
      "additionalProperties": false,
      "properties": {
        "slide_id": {
          "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
          "title": "Slide Id",
          "type": "string"
        },
        "type": {
          "const": "after",
          "default": "after",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "slide_id"
      ],
      "title": "InsertAfter",
      "type": "object"
    },
    "InsertBefore": {
      "additionalProperties": false,
      "properties": {
        "slide_id": {
          "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
          "title": "Slide Id",
          "type": "string"
        },
        "type": {
          "const": "before",
          "default": "before",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "slide_id"
      ],
      "title": "InsertBefore",
      "type": "object"
    },
    "InsertEnd": {
      "additionalProperties": false,
      "properties": {
        "type": {
          "const": "end",
          "default": "end",
          "title": "Type",
          "type": "string"
        }
      },
      "title": "InsertEnd",
      "type": "object"
    },
    "InsertStart": {
      "additionalProperties": false,
      "properties": {
        "type": {
          "const": "start",
          "default": "start",
          "title": "Type",
          "type": "string"
        }
      },
      "title": "InsertStart",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "description": {
      "anyOf": [
        {
          "maxLength": 240,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Description"
    },
    "expected_revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Revision"
    },
    "name": {
      "maxLength": 80,
      "minLength": 1,
      "title": "Name",
      "type": "string"
    },
    "position": {
      "anyOf": [
        {
          "discriminator": {
            "mapping": {
              "after": "#/$defs/InsertAfter",
              "before": "#/$defs/InsertBefore",
              "end": "#/$defs/InsertEnd",
              "start": "#/$defs/InsertStart"
            },
            "propertyName": "type"
          },
          "oneOf": [
            {
              "$ref": "#/$defs/InsertStart"
            },
            {
              "$ref": "#/$defs/InsertEnd"
            },
            {
              "$ref": "#/$defs/InsertBefore"
            },
            {
              "$ref": "#/$defs/InsertAfter"
            }
          ]
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Position"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "slide_id",
    "name"
  ],
  "title": "slide_duplicateArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "$defs": {
    "SlideRef": {
      "additionalProperties": false,
      "properties": {
        "description": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Description"
        },
        "name": {
          "title": "Name",
          "type": "string"
        },
        "number": {
          "minimum": 1,
          "title": "Number",
          "type": "integer"
        },
        "slide_id": {
          "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
          "title": "Slide Id",
          "type": "string"
        }
      },
      "required": [
        "slide_id",
        "number",
        "name"
      ],
      "title": "SlideRef",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "previous_revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Previous Revision",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "slide": {
      "$ref": "#/$defs/SlideRef"
    }
  },
  "required": [
    "presentation_id",
    "previous_revision",
    "revision",
    "slide"
  ],
  "title": "SlideDuplicateResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": false,
  "idempotentHint": false,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

### `slide_delete` — Delete slides

Delete one or more slides atomically.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "expected_revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Revision"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "slide_ids": {
      "items": {
        "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
        "type": "string"
      },
      "maxItems": 100,
      "minItems": 1,
      "title": "Slide Ids",
      "type": "array"
    }
  },
  "required": [
    "presentation_id",
    "slide_ids"
  ],
  "title": "slide_deleteArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "additionalProperties": false,
  "properties": {
    "deleted_slide_ids": {
      "items": {
        "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
        "type": "string"
      },
      "title": "Deleted Slide Ids",
      "type": "array"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "previous_revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Previous Revision",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "slide_count": {
      "title": "Slide Count",
      "type": "integer"
    }
  },
  "required": [
    "presentation_id",
    "previous_revision",
    "revision",
    "deleted_slide_ids",
    "slide_count"
  ],
  "title": "SlideDeleteResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": true,
  "idempotentHint": true,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

### `slide_reorder` — Reorder slides

Set the complete declarative slide order using every current stable slide ID exactly once.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "expected_revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Revision"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "slide_ids": {
      "items": {
        "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
        "type": "string"
      },
      "maxItems": 500,
      "minItems": 1,
      "title": "Slide Ids",
      "type": "array"
    }
  },
  "required": [
    "presentation_id",
    "slide_ids"
  ],
  "title": "slide_reorderArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "$defs": {
    "SlideRef": {
      "additionalProperties": false,
      "properties": {
        "description": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Description"
        },
        "name": {
          "title": "Name",
          "type": "string"
        },
        "number": {
          "minimum": 1,
          "title": "Number",
          "type": "integer"
        },
        "slide_id": {
          "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
          "title": "Slide Id",
          "type": "string"
        }
      },
      "required": [
        "slide_id",
        "number",
        "name"
      ],
      "title": "SlideRef",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "previous_revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Previous Revision",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "slides": {
      "items": {
        "$ref": "#/$defs/SlideRef"
      },
      "title": "Slides",
      "type": "array"
    }
  },
  "required": [
    "presentation_id",
    "previous_revision",
    "revision",
    "slides"
  ],
  "title": "SlideReorderResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": false,
  "idempotentHint": true,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

### `element_inspect` — Inspect element

Inspect one stable element subtree, attributes, and inline styles.

Input schema:

```json
{
  "$defs": {
    "ElementById": {
      "additionalProperties": false,
      "properties": {
        "element_id": {
          "pattern": "^el_[A-Za-z0-9_-]{8,}$",
          "title": "Element Id",
          "type": "string"
        },
        "type": {
          "const": "id",
          "default": "id",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "element_id"
      ],
      "title": "ElementById",
      "type": "object"
    },
    "ElementByName": {
      "additionalProperties": false,
      "properties": {
        "element_name": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Element Name",
          "type": "string"
        },
        "type": {
          "const": "name",
          "default": "name",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "element_name"
      ],
      "title": "ElementByName",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "depth": {
      "default": 1,
      "maximum": 10,
      "minimum": 0,
      "title": "Depth",
      "type": "integer"
    },
    "element": {
      "discriminator": {
        "mapping": {
          "id": "#/$defs/ElementById",
          "name": "#/$defs/ElementByName"
        },
        "propertyName": "type"
      },
      "oneOf": [
        {
          "$ref": "#/$defs/ElementById"
        },
        {
          "$ref": "#/$defs/ElementByName"
        }
      ],
      "title": "Element"
    },
    "include_html": {
      "default": true,
      "title": "Include Html",
      "type": "boolean"
    },
    "include_styles": {
      "default": true,
      "title": "Include Styles",
      "type": "boolean"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Revision"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "slide_id",
    "element"
  ],
  "title": "element_inspectArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "additionalProperties": false,
  "properties": {
    "attributes": {
      "additionalProperties": {
        "type": "string"
      },
      "title": "Attributes",
      "type": "object"
    },
    "child_ids": {
      "items": {
        "pattern": "^el_[A-Za-z0-9_-]{8,}$",
        "type": "string"
      },
      "title": "Child Ids",
      "type": "array"
    },
    "element_id": {
      "pattern": "^el_[A-Za-z0-9_-]{8,}$",
      "title": "Element Id",
      "type": "string"
    },
    "element_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "title": "Element Name"
    },
    "html": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "title": "Html"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    },
    "styles": {
      "anyOf": [
        {
          "additionalProperties": {
            "type": "string"
          },
          "type": "object"
        },
        {
          "type": "null"
        }
      ],
      "title": "Styles"
    },
    "tag": {
      "title": "Tag",
      "type": "string"
    },
    "text": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "title": "Text"
    }
  },
  "required": [
    "presentation_id",
    "revision",
    "slide_id",
    "element_id",
    "element_name",
    "tag",
    "text",
    "attributes",
    "styles",
    "html",
    "child_ids"
  ],
  "title": "ElementInspectResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": null,
  "idempotentHint": null,
  "openWorldHint": false,
  "readOnlyHint": true,
  "title": null
}
```

### `element_add` — Add element

Insert a safe inline-styled HTML subtree relative to a stable element.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    },
    "ElementById": {
      "additionalProperties": false,
      "properties": {
        "element_id": {
          "pattern": "^el_[A-Za-z0-9_-]{8,}$",
          "title": "Element Id",
          "type": "string"
        },
        "type": {
          "const": "id",
          "default": "id",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "element_id"
      ],
      "title": "ElementById",
      "type": "object"
    },
    "ElementByName": {
      "additionalProperties": false,
      "properties": {
        "element_name": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Element Name",
          "type": "string"
        },
        "type": {
          "const": "name",
          "default": "name",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "element_name"
      ],
      "title": "ElementByName",
      "type": "object"
    },
    "ElementInsertPosition": {
      "enum": [
        "before",
        "after",
        "prepend",
        "append"
      ],
      "title": "ElementInsertPosition",
      "type": "string"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "expected_revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Revision"
    },
    "html": {
      "minLength": 1,
      "title": "Html",
      "type": "string"
    },
    "position": {
      "$ref": "#/$defs/ElementInsertPosition"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "relative_to": {
      "discriminator": {
        "mapping": {
          "id": "#/$defs/ElementById",
          "name": "#/$defs/ElementByName"
        },
        "propertyName": "type"
      },
      "oneOf": [
        {
          "$ref": "#/$defs/ElementById"
        },
        {
          "$ref": "#/$defs/ElementByName"
        }
      ],
      "title": "Relative To"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "slide_id",
    "relative_to",
    "position",
    "html"
  ],
  "title": "element_addArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "$defs": {
    "AddedElement": {
      "additionalProperties": false,
      "properties": {
        "element_id": {
          "pattern": "^el_[A-Za-z0-9_-]{8,}$",
          "title": "Element Id",
          "type": "string"
        },
        "element_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Element Name"
        },
        "tag": {
          "title": "Tag",
          "type": "string"
        }
      },
      "required": [
        "element_id",
        "element_name",
        "tag"
      ],
      "title": "AddedElement",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "previous_revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Previous Revision",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "roots": {
      "items": {
        "$ref": "#/$defs/AddedElement"
      },
      "title": "Roots",
      "type": "array"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "previous_revision",
    "revision",
    "slide_id",
    "roots"
  ],
  "title": "ElementAddResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": false,
  "idempotentHint": false,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

### `element_update` — Update elements

Atomically update one or more elements. Use for normal text, style, attribute, or subtree edits.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    },
    "AttributeMutation": {
      "additionalProperties": false,
      "properties": {
        "remove": {
          "items": {
            "type": "string"
          },
          "maxItems": 100,
          "title": "Remove",
          "type": "array"
        },
        "set": {
          "additionalProperties": {
            "type": "string"
          },
          "maxProperties": 100,
          "title": "Set",
          "type": "object"
        }
      },
      "title": "AttributeMutation",
      "type": "object"
    },
    "ElementById": {
      "additionalProperties": false,
      "properties": {
        "element_id": {
          "pattern": "^el_[A-Za-z0-9_-]{8,}$",
          "title": "Element Id",
          "type": "string"
        },
        "type": {
          "const": "id",
          "default": "id",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "element_id"
      ],
      "title": "ElementById",
      "type": "object"
    },
    "ElementByName": {
      "additionalProperties": false,
      "properties": {
        "element_name": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Element Name",
          "type": "string"
        },
        "type": {
          "const": "name",
          "default": "name",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "element_name"
      ],
      "title": "ElementByName",
      "type": "object"
    },
    "ElementMutation": {
      "additionalProperties": false,
      "properties": {
        "attributes": {
          "anyOf": [
            {
              "$ref": "#/$defs/AttributeMutation"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "element": {
          "discriminator": {
            "mapping": {
              "id": "#/$defs/ElementById",
              "name": "#/$defs/ElementByName"
            },
            "propertyName": "type"
          },
          "oneOf": [
            {
              "$ref": "#/$defs/ElementById"
            },
            {
              "$ref": "#/$defs/ElementByName"
            }
          ],
          "title": "Element"
        },
        "inner_html": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Inner Html"
        },
        "replace_html": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Replace Html"
        },
        "styles": {
          "anyOf": [
            {
              "$ref": "#/$defs/StyleMutation"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "text": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Text"
        }
      },
      "required": [
        "element"
      ],
      "title": "ElementMutation",
      "type": "object"
    },
    "StyleMutation": {
      "additionalProperties": false,
      "properties": {
        "remove": {
          "items": {
            "type": "string"
          },
          "maxItems": 100,
          "title": "Remove",
          "type": "array"
        },
        "set": {
          "additionalProperties": {
            "type": "string"
          },
          "maxProperties": 100,
          "title": "Set",
          "type": "object"
        }
      },
      "title": "StyleMutation",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "elements": {
      "items": {
        "$ref": "#/$defs/ElementMutation"
      },
      "maxItems": 100,
      "minItems": 1,
      "title": "Elements",
      "type": "array"
    },
    "expected_revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Revision"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "slide_id",
    "elements"
  ],
  "title": "element_updateArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "additionalProperties": false,
  "properties": {
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "previous_revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Previous Revision",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    },
    "updated_element_ids": {
      "items": {
        "pattern": "^el_[A-Za-z0-9_-]{8,}$",
        "type": "string"
      },
      "title": "Updated Element Ids",
      "type": "array"
    }
  },
  "required": [
    "presentation_id",
    "previous_revision",
    "revision",
    "slide_id",
    "updated_element_ids"
  ],
  "title": "ElementUpdateResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": false,
  "idempotentHint": false,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

### `element_move` — Move elements

Move elements in DOM hierarchy/order; pixel geometry remains inline CSS.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    },
    "ElementById": {
      "additionalProperties": false,
      "properties": {
        "element_id": {
          "pattern": "^el_[A-Za-z0-9_-]{8,}$",
          "title": "Element Id",
          "type": "string"
        },
        "type": {
          "const": "id",
          "default": "id",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "element_id"
      ],
      "title": "ElementById",
      "type": "object"
    },
    "ElementByName": {
      "additionalProperties": false,
      "properties": {
        "element_name": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Element Name",
          "type": "string"
        },
        "type": {
          "const": "name",
          "default": "name",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "element_name"
      ],
      "title": "ElementByName",
      "type": "object"
    },
    "ElementInsertPosition": {
      "enum": [
        "before",
        "after",
        "prepend",
        "append"
      ],
      "title": "ElementInsertPosition",
      "type": "string"
    },
    "ElementMoveOperation": {
      "additionalProperties": false,
      "properties": {
        "element": {
          "discriminator": {
            "mapping": {
              "id": "#/$defs/ElementById",
              "name": "#/$defs/ElementByName"
            },
            "propertyName": "type"
          },
          "oneOf": [
            {
              "$ref": "#/$defs/ElementById"
            },
            {
              "$ref": "#/$defs/ElementByName"
            }
          ],
          "title": "Element"
        },
        "position": {
          "$ref": "#/$defs/ElementInsertPosition"
        },
        "relative_to": {
          "discriminator": {
            "mapping": {
              "id": "#/$defs/ElementById",
              "name": "#/$defs/ElementByName"
            },
            "propertyName": "type"
          },
          "oneOf": [
            {
              "$ref": "#/$defs/ElementById"
            },
            {
              "$ref": "#/$defs/ElementByName"
            }
          ],
          "title": "Relative To"
        }
      },
      "required": [
        "element",
        "relative_to",
        "position"
      ],
      "title": "ElementMoveOperation",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "expected_revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Revision"
    },
    "moves": {
      "items": {
        "$ref": "#/$defs/ElementMoveOperation"
      },
      "maxItems": 50,
      "minItems": 1,
      "title": "Moves",
      "type": "array"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "slide_id",
    "moves"
  ],
  "title": "element_moveArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "additionalProperties": false,
  "properties": {
    "moved_element_ids": {
      "items": {
        "pattern": "^el_[A-Za-z0-9_-]{8,}$",
        "type": "string"
      },
      "title": "Moved Element Ids",
      "type": "array"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "previous_revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Previous Revision",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "previous_revision",
    "revision",
    "slide_id",
    "moved_element_ids"
  ],
  "title": "ElementMoveResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": false,
  "idempotentHint": false,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

### `element_delete` — Delete elements

Delete one or more stable slide elements atomically.

Input schema:

```json
{
  "$defs": {
    "Activity": {
      "additionalProperties": false,
      "properties": {
        "label": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "label"
      ],
      "title": "Activity",
      "type": "object"
    },
    "ElementById": {
      "additionalProperties": false,
      "properties": {
        "element_id": {
          "pattern": "^el_[A-Za-z0-9_-]{8,}$",
          "title": "Element Id",
          "type": "string"
        },
        "type": {
          "const": "id",
          "default": "id",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "element_id"
      ],
      "title": "ElementById",
      "type": "object"
    },
    "ElementByName": {
      "additionalProperties": false,
      "properties": {
        "element_name": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Element Name",
          "type": "string"
        },
        "type": {
          "const": "name",
          "default": "name",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "element_name"
      ],
      "title": "ElementByName",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "activity": {
      "anyOf": [
        {
          "$ref": "#/$defs/Activity"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "elements": {
      "items": {
        "discriminator": {
          "mapping": {
            "id": "#/$defs/ElementById",
            "name": "#/$defs/ElementByName"
          },
          "propertyName": "type"
        },
        "oneOf": [
          {
            "$ref": "#/$defs/ElementById"
          },
          {
            "$ref": "#/$defs/ElementByName"
          }
        ]
      },
      "maxItems": 100,
      "minItems": 1,
      "title": "Elements",
      "type": "array"
    },
    "expected_revision": {
      "anyOf": [
        {
          "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Revision"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "slide_id",
    "elements"
  ],
  "title": "element_deleteArguments",
  "type": "object"
}
```

Output schema:

```json
{
  "additionalProperties": false,
  "properties": {
    "deleted_element_ids": {
      "items": {
        "pattern": "^el_[A-Za-z0-9_-]{8,}$",
        "type": "string"
      },
      "title": "Deleted Element Ids",
      "type": "array"
    },
    "presentation_id": {
      "pattern": "^prs_[A-Za-z0-9_-]{8,}$",
      "title": "Presentation Id",
      "type": "string"
    },
    "previous_revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Previous Revision",
      "type": "string"
    },
    "revision": {
      "pattern": "^rev_[A-Za-z0-9_-]{8,}$",
      "title": "Revision",
      "type": "string"
    },
    "slide_id": {
      "pattern": "^sld_[A-Za-z0-9_-]{8,}$",
      "title": "Slide Id",
      "type": "string"
    }
  },
  "required": [
    "presentation_id",
    "previous_revision",
    "revision",
    "slide_id",
    "deleted_element_ids"
  ],
  "title": "ElementDeleteResult",
  "type": "object"
}
```

Annotations:

```json
{
  "destructiveHint": true,
  "idempotentHint": true,
  "openWorldHint": false,
  "readOnlyHint": false,
  "title": null
}
```

## Resource templates

- `office://presentations/{presentation_id}` — Presentation metadata
- `office://presentations/{presentation_id}/outline` — Presentation outline
- `office://presentations/{presentation_id}/validation` — Presentation validation
- `office://presentations/{presentation_id}/preview{?quality,labels,columns}` — Presentation preview
- `office://presentations/{presentation_id}/revisions/{revision_id}` — Presentation revision
- `office://presentations/{presentation_id}/revisions/{revision_id}/file` — PowerPoint revision file
- `office://presentations/{presentation_id}/slides/{slide_id}` — Slide structure
- `office://presentations/{presentation_id}/slides/{slide_id}/source` — Slide source
- `office://presentations/{presentation_id}/slides/{slide_id}/preview{?quality}` — Slide preview
- `office://presentations/{presentation_id}/slides/{slide_id}/elements/{element_id}` — Slide element

## Prompts

- `create_presentation` — Create presentation; arguments: topic, audience, purpose, style, slide_count
- `review_presentation` — Review presentation; arguments: presentation_id, focus

## Completion-enabled arguments

- `presentation_id`
- `slide_id` (dependent on `presentation_id`)
- `element_id` (dependent on `presentation_id` and `slide_id`)
