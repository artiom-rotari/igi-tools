from igipy.config import Settings
from igipy.tex.models import TEX

settings = Settings.load()
settings.is_valid()


tex_9_exclude = {"content": {"bitmaps": {"__all__": {"data": True}}}}


def parse_terrain_textures():
    return [TEX.model_validate_file(src) for src in settings.game_dir.glob("**/**/terrain/terrain.tex")]


textures = parse_terrain_textures()


for texture in textures:
    print(texture.content.model_dump(exclude={"sub_headers": True, "bitmaps": True, "footer": True}))


for texture in textures:
    for subheader in texture.content.sub_headers:
        print(subheader.model_dump())
    print()


for texture in textures:
    for bitmap in texture.content.bitmaps:
        print(bitmap.model_dump(exclude={"data": True}))
    print()
