[![texconv.exe](https://img.shields.io/github/downloads/Microsoft/DirectXTex/latest/texconv.exe?style=for-the-badge)](https://github.com/Microsoft/DirectXTex/releases/latest/download/texconv.exe)

This DirectXTex sample is an implementation of the **texconv** command-line texture utility from the legacy DirectX SDK utilizing DirectXTex rather than D3DX. This tool loads an image and prepares it for runtime use by resizing, format conversion, mip-map generation, block-compression, and writes the result in a file format suited for runtime use. It can also be used for other image-to-image processing.

> To create cubemaps, volume maps, or texture arrays from individual files, use [[Texassemble]].

*The 'texconv' in the [Azure Remote Rendering](https://docs.microsoft.com/azure/remote-rendering/) tooling is completely unrelated to this 'texconv' tool.*

# Syntax
``Texconv.exe`` uses the following command syntax:

```
texconv [options] [--file-list <filename>] <file-name(s)>
```

The file-name parameter indicates the file(s) to convert using ``dds``, ``tga``, ``hdr``, ``phm``, ``ppm``, ``pfm``, or a WIC-supported format (``bmp``, ``jpg``, ``png``, ``jxr``, ``heif``, ``wepb``, etc.).

> The command-line parsing uses Windows-style `-` or `/` for options. It also has some POSIX-like behavior: it supports ``--version`` and ``--help`` command-line options, and the use of ``--`` disables further options parsing to support filenames that begin with `-` or `/` characters. There are 'GNU long options' style command-line parameters that use ``--`` as well.

# Optional Switches Description

## File options

**-r**: Input file names can contain wildcard characters (``?`` or ``*``). If this switch is used, subdirectories are also searched. If ``-r:keep`` is specified, then the output directory includes the subdirectory structure of the source tree. If no option is specified or ``-r:flatten`` is used, then the resulting output directory just includes the files.

**-flist _filename_**, **--file-list _filename_**: Uses the provided filename as a text file containing a list of input files (one per line). Ignores lines that begin with ``#`` (used for comments). Does not support providing additional command-line arguments or the use of filename wildcards.

**-px _string_**, **--prefix _string_**: Text string to attach to the front of the resulting texture's name.   
**-sx _string_**, **--suffix _string_**: Text string to attach to the end of the resulting texture's name.

**-o _directory_**: Output directory.

**-l**, **--to-lowercase**: Forces the output path & filename to all lower-case. *Windows file system is case-insensitive by default, but some programs like git are case-sensitive*.

**-y**, **--overwrite**: overwrite existing output file if any. By default, the tool will skip the write if the output file already exists.


## File and pixel format options

**-ft _file-type_**, **--file-type _file-type_**: A file type for the output texture. Use one of the following. The default value is ``dds``.
 * ``bmp``: Windows BMP
 *  ``jpg``, ``jpeg``: Joint Photographic Experts Group
 * ``png``: Portable Network Graphics
 * ``dds``, ``ddx``: DirectDraw Surface (Direct3D texture file format)
 * ``tga``: Truevision Graphics Adapter
 * ``hdr``: Radiance RGBE
 * ``tif``, ``tiff``:  Tagged Image File Format
 *  ``wdp``, ``hdp``, ``jxr``: Windows Media Photo
 * ``ppm``, ``pfm``: Portable PixMap, Portable FloatMap (Netpbm)

**-f _format_**. **--format _format_**: Output format. Specify the DXGI format without the ``DXGI_FORMAT_`` prefix (i.e. ``-f R10G10B10A2_UNORM``). It also supports some common aliases (``-f DXT1`` for ``DXGI_FORMAT_BC1_UNORM``, ``-f DXT5`` for ``DXGI_FORMAT_BC3_UNORM``, ``-f BGRA`` for ``DXGI_FORMAT_B8G8R8A8_UNORM``, ``-f BGR`` for ``DXGI_FORMAT_B8G8R8X8_UNORM``, ``-f FP16`` for ``DXGI_FORMAT_R16G16B16A16_FLOAT``, etc.). See *Remarks*.

## Resizing and mipmap options

**-w _number_**, **--width _number_**: Width of the output texture in pixels.   
**-h _number_**, **--height _number_**: Height of the output texture in pixels. If no size is given, the size is taken from the first input image.

**-m _number_**, **--mip-levels _number_**: Number of mipmap levels to generate in the output texture. This setting only applies to DDS output, which defaults to 0 which is generate all mipmaps. Use ``-m 1`` to remove mipmaps.

**-pow2**, **--fit-power-of-2**: Fits each texture to a power-of-2 for width & height, minimizing changes to the aspect ratio. The maximum size for a dimension is based on the ``-fl`` switch (defaults to 16384).


## Filtering options

**-if _filter_**, **--image-filter _filter_**: Image filter used for resizing the images. Use one of the following: ``POINT``, ``LINEAR``, ``CUBIC``, ``FANT``, ``BOX``, ``TRIANGLE``, ``POINT_DITHER``, ``LINEAR_DITHER``, ``CUBIC_DITHER``, ``FANT_DITHER``, ``BOX_DITHER``, ``TRIANGLE_DITHER``, ``POINT_DITHER_DIFFUSION``, ``LINEAR_DITHER_DIFFUSION``, ``CUBIC_DITHER_DIFFUSION``, ``FANT_DITHER_DIFFUSION``, ``BOX_DITHER_DIFFUSION``, or ``TRIANGLE_DITHER_DIFFUSION``. Filters with ``DITHER`` in their name indicate that the 4x4 ordered dither algorithm, while ``DITHER_DIFFUSION`` is error diffusion dithering.

**-wrap**, **-mirror**: Sets the texture addressing mode for filtering to wrap or mirror, otherwise defaults to clamp.

**-nowic**: Forces filtering to use non-WIC-based code paths. This is useful for working around known issues with WIC depending on which operating system you are using.


## Colorspace options

**-srgb**, **-srgbi** / **--srgb-in**, or **-srgbo** / **--srgb-out**: Use sRGB if both the input and output data are in the sRGB color format (ie. gamma ~2.2). Use sRGBi if only the input is in sRGB; use sRGBo if only the output is in sRGB.

**--rotate-color _rot_**: Performs color rotations and/or ST.2084 curves for converting image data to/from HDR10 signals.

  * _709to2020_: Converts from Rec.709 color primaries to Rec.2020 color primaries.
  * _2020to709_: Converts from Rec.2020 color primaries to Rec.709 color primaries.
  * _709toHDR10_: Converts from Rec.709 color primaries to Rec.2020, normalizing nits, and applying the ST.2084 curve to create an HDR10 signal.
  * _HDR10to709_: Converts an HDR10 signal back to Rec.709 color primaries with linear values.
  * _P3to2020_: Converts from DCI-P3 color primaries to Rec.2020 color primaries.
  * _P3toHDR10_: Converts from DCI-P3 color primaries to Rec.2020, normalizing nits, and applying the ST.2084 curve to create an HDR10 signal.
  * _709toDisplayP3_: Converts from Rec.709 color primaries to Display-P3 (D65 white point)
  * _DisplayP3to709_: Converts from Display-P3 (D65 white point) to Rec.709 color primaries.

**-nits _number_**, **--paper-white-nits _number_**: Provides a paper-white nits value for the HDR10 conversions above (defaults to 200.0) with an upper limit of 10000.

**--tonemap**: Applies a *Reinhard tonemap operator* based on maximum luminosity to ensure HDR image data is adjusted to an LDR range.

**--ignore-srgb**: When reading an image from the various WIC formats or `TGA`, this flag indicates that any metadata about color-space in the file should be ignored and the resulting format is never ``DXGI_FORMAT_*_SRGB``.

## Alpha options

**-pmalpha**, **--premultiplied-alpha**: Converts the final texture data to use premultiplied alpha. This sets an alpha mode of ``DDS_ALPHA_MODE_PREMULTIPLIED`` unless the entire alpha channel is fully opaque.

**-alpha**: Converts a premultiplied alpha image to non-premultiplied alpha (a.k.a. straight alpha).

**-sepalpha**, **--separate-alpha**: Separates alpha channel for resize/mipmap generation. This implies an alpha mode setting of ``DDS_ALPHA_MODE_CUSTOM`` as this is typically only used if the alpha channel doesn't contain transparency information.

> Without this flag, anywhere you have a 0 in the alpha channel, the RGB will be zero because of the fact that WIC operates with premultiplied-alpha. If the alpha channel is actually transparency, the default behavior works fine.

**-at _number_**, **--alpha-threshold _number_**: Sets the alpha threshold value for 1-bit alpha such as BC1 or RGBA5551. Defaults to 0.5.

**--keep-coverage _number_**: Preserves alpha coverage in generate mipmaps for alpha test reference value (0 to 1).

**-c _color_**, **--color-key _color_**: Provides a colorkey/[chromakey](https://wikipedia.org/wiki/Chroma_key) value which is used to replace a specific RGB color in hexadecimal (within a tolerance) with alpha 0.0. Any existing color channel is overwritten. For example, ``-c 0000FF`` for a blue colorkey, ``-c 00FF00`` for a green colorkey, ``-c 0CFF5D`` for the typical 'green-screen' in a video.


## Block Compression (BC) options

**--single-proc**: If the DirectXTex library and the texconv utility are built with OpenMP enabled, by default the tool will use multi-threading for CPU-based compression of BC6H and BC7 formats to spread the compression work across multiple cores. This flag disables this behavior forcing it to remain on a single core.

**-gpu _adapterIndex_**: When compressing BC6H / BC7 content, texconv will use DirectCompute on the GPU at the given index if available. The default is 0 which is the default adapter.

**-nogpu**: When compressing BC6H / BC7 content, texconv will use DirectCompute on the GPU if available. Use of this flag forces texconv to always use the software codec instead.

**-bc _flags_**, **--block-compress _flags_**: Sets options for BC compression. The flags is a combination of one or more of the following:
 * **u**: to use uniform weighting rather than perceptual (BC1-BC3)
 * **d**: use dithering (BC1-BC3)
 * **q**: Uses minimal compression (BC7: uses just mode 6)
 * **x**: Uses maximum compression (BC7: enables mode 0 & 2 usage)

**-aw _number_**, **--alpha-weight _number_**: Provides an alpha weighting to use with the error metric for the BC7 GPU compressor. Defaults to 1.0.



## Normal-map generation options

**-nmap _flags_**, **--normal-map _flags_**: Indicates conversion from a height-map to a normal-map. The flags is a combination of one or more of the following, and must have one of r, g, b, a, or l:

 * **r**: Use the red channel of the input as the height
 * **g**: Use the green channel of the input as the height
 * **b**: Use the blue channel of the input as the height
 * **a**: Use the alpha channel of the input as the height
 * **l**: Use the luminance computed from red, green, and blue channels of the input as the height
 * **m**: Use mirroring in U & V. Defaults to wrap when doing the central difference computation.
 * **u**: Use mirroring in U. Defaults to wrap when doing the central difference computation.
 * **v**: Use mirroring in V. Defaults to wrap when doing the central difference computation.
 * **i**: Invert sign of the computed normal
 * **o**: Compute a rough occlusion term and encode it into the alpha channel of the output.

**-nmapamp _number_**, **--normal-map-amplitude _number_**: Indicates an amplitude for the normal map, which defaults to 1.

> Remember that the output format defaults to the input format, so be sure to use ``-f`` if you want a different output format. See [[ComputeNormalMap]] for more information.

**--invert-y**: Inverts the value of the green channel. This is typically used for normal maps to deal with OpenGL vs. Direct3D conventions for 'push in' vs. 'push out'.

**--reconstruct-z**: Rebuilds the Z (blue) channel assuming X/Y are normals (primarily for converting from the BC5 format)

**--x2-bias**: Enables special ``*2 -1`` conversion cases for converting unorm <-> float, and positive-only-floats <-> float/snorm. These are typically used with normal maps.


## Image operation options

**-hflip**, **--horizontal-flip**: Perform horizonal flip of image   
**-vflip**, **--vertical-flip**: Perform horizonal flip of image

**--swizzle _rgbamask_**: Swizzles image channels using an [HLSL-style](https://docs.microsoft.com/windows/win32/direct3dhlsl/dx9-graphics-reference-asm-ps-registers-modifiers-source-register-swizzling) mask (``rgba``, ``rrra``, ``r``, ``a``, ``xy``, etc.). The mask is 1 to 4 characters in length. A ``0`` indicates setting that channel to zero, a ``1`` indicates setting that channel to maximum.


## Windows Image Component (WIC) options

**-wicq _number_**, **--wic-quality _number_**: Provides an image quality setting to use when encoding WIC images ranging from 0.0 to 1.0. Applies to ``jpg``, ``tif``, ``heif``, and ``jxr``.

**--wic-lossless**: Enable lossless encoding when encoding WIC images. Applies to ``jxr``. This ignores any value for *wic-quality*.

**--wic-uncompressed**: Enable uncompressed encoding for WIC images. Applies to `tif` and `heif`. This ignores any value for *wic-quality*.

**--wic-multiframe**: When encoding WIC images, the use of this flag will encode multiframe images. By default it writes only the first frame like the ``hdr`` and``tga`` writers. Note that only some WIC containers support multiframe images (notably ``gif`` and ``tif``).


## DirectDraw Surface (DDS) file options

**-tu**, **--typeless-unorm**: DDS files with TYPELESS formats are treated as UNORM
**-tf**, **--typeless-float**: DDS files with TYPELESS formats are treated as FLOAT

> Generally typeless formats will fail most operations, so these options let you override the type.

**-dword**, **--dword-alignment*: For DDS files that use a DWORD alignment instead of BYTE alignment (used for some legacy files typically 24bpp).

**--bad-tails**: For older DDS files that incorrectly encode the DXTn block compression mipchain surface blocks smaller than 4x4. This switch causes the loader to tolerate the slightly too short file length and to copy the 4x4 blocks to the smaller ones. The result is not identical to re-computing computing the mipchain fully, but does provide non-corrupted data.

**--permissive**: Allows some malformed and variant header files to be loaded.

**--ignore-mips**: Loads only the top-level mipmap, which is useful for some malformed files that are missing data.

**--fix-bc-4x4**: DDS files can contain BC compressed DDS files of arbitrary size, but Direct3D can only create BC resources where the top-level width & height are multiples of 4. This switch will resize the image to the proper size for loading as a texture, but any mipmaps will have to be regenerated.

**-xlum**, **--expand-luminance**: DDS files with L8, A8L8, or L16 formats are expanded to 8:8:8:8 or 16:16:16:16. Without this flag, they are converted to 1-channel (red) or 2-channel (red/green) formats.

**-dx10**: Forces DDS file output to always use the "DX10" header extension, and allows the writing of alpha mode metadata information. The resulting file may not be compatible with the legacy D3DX10 or D3DX11 libraries or older DDS readers.

**-dx9**: Forces DDS file output to always use legacy DX9 headers. This will fail for ``BC6``, ``BC7``, ``UINT``, and ``SINT`` formats. ``SRGB`` formats will be written using non-SRGB formats. It will also fail for texture 2D arrays and cubemap arrays. *This is primarily of use with DX9 era DDS texture loaders.*


## Targa TruVision (TGA) file options

**-tga20**: Forces TGA file output to include the TGA 2.0 extension area which includes gamma, alpha mode, and a time stamp.

**--tga-zero-alpha**: By default a TGA file with an alpha channel of all zeros is treated as 'opaque' which results in all ones for the alpha channel if present. With this switch, all zero alpha channels will be returned in their original form instead.


## Direct3D options

**-fl _feature-level_**, **--feature-level _feature-level_**: Sets the target feature level which determines the maximum supported texture size: ``9.1``, ``9.2``, ``9.3``, ``10.0``, ``10.1``, ``11.0``, ``11.1``, ``12.0``, ``12.1``, or ``12.2``. Defaults to ``11.0`` which is 16834, the limit for 11.x and 12.x [Direct3D Hardware Feature Level](https://aka.ms/Apsgrj).

## Miscellaneous options

**-nologo**: Suppress copyright message.

**--timing**: Displays compression timing information


# Examples
Open a Command Prompt, and change to the directory containing Texconv.exe (i.e. `...\DirectXTex\Texconv\Release`)

Enter the following command-line after changing to the appropriate directory:

```
texconv -pow2 -f BC1_UNORM cat.jpg
```

This loads a JPEG image 'cat.jpg', resizes the image to a power of 2 in each dimension (if the original was 512 x 683 it is resized to 256 x 512), mipmaps are generated, the file is converted to ``DXGI_FORMAT_BC1_UNORM`` (aka DXT1) block compression, and written out as 'cat.dds'.

```
texconv -r C:\Textures\*.png
```

This converts all the ``.png`` files in the ``C:\Textures`` directory tree to ``dds`` files written into the current working directory.

```
texconv -nmap lo -nmapamp 2 -f R8G8B8A8_UNORM heightmap.png
```

This loads the PNG image 'heightmap.png', converts it to a normal-map using luminance and an amplitude of 2, and writes the data out as a 'heightmap.dds' with mipmaps and an occlusion term in the alpha channel using the ``DXGI_FORMAT_R8G8B8A8_UNORM`` format.

```
texconv myimage.hdr -tonemap -ft BMP
```

This loads the HDR (Radiance RGBE) image `myimage.hdr`, performs a tone-mapping operation, and then writes the result to `myimage.bmp`.

```
texconv -pow2 -fl 9.3 -f BC3_UNORM -m 1 *.bmp
```

This creates a ``DDS`` file for each ``BMP`` file in the current directory that is sized to a power-of-2 respecting aspect ratio with a maximum size of 4096 for a given dimension. The results are compressed as ``DXGI_FORMAT_BC3_UNORM`` (a.k.a. DXT5) and have no mipmaps.

# Remarks

When loading ``BMP`` files, if the WIC codec fails to load the image, the _texconv_ tool will check to see if it's an [Extended BMP](http://www.mwgfx.co.uk/NewBmp/tech.htm) containing ``DXT1``, ``DXT3``, or ``DXT5`` compressed data. The tool does not support writing Extended BMP files. Typically you need to use ``-vflip`` with such files as well.

Support for [OpenEXR](http://www.openexr.com/) (``EXR``) can be added to the *texconv* utility. Uncomment ``#define USE_OPENEXR`` in the source, and add the DirectXTex auxiliary module to the project. See [[Adding OpenEXR]] for more details including building the OpenEXR library. This adds ``exr`` as an option for ``-ft``.

The texconv tool supports any additional installed WIC codec. For example, if you install the [HEIF WIC Codec](https://aka.ms/heif), the tool can successfully read ``.heif`` or ``.heic`` images, and use ``.heif`` as an option for ``-ft``. If you install the [WEBP Codec](https://apps.microsoft.com/detail/9PG2DK419DRG), the tool can read ``.webp`` files--this codec does not support writing ``.webp`` files.

The tool supports writing some special variant cases when provided as the output format which should be combined with `-dx9` to force legacy DDS header structures.

* `-f BC3n` or `-f DXT5nm`: This is a DXT5 variant which swaps color channels to improve normal-map compression before BC4/BC5 was widely available. See the article *Real-Time Normal Map DXT Compression* (2008) for details.
* `-f RXGB -dx9`: This is a custom FourCC with another legacy DXT5 variant style for normal-maps which requires less reconstruction required in the shader.

# Further reading

Reinhard et al., "Photographic tone reproduction for digital images", *ACM Transactions on Graphics*, Volume 21, Issue 3 (July 2002). [ACM DL](https://dl.acm.org/doi/10.1145/566654.566575).