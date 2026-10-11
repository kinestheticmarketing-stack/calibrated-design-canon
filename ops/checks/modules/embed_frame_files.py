"""embed_frame_files -- every calculator slug has its embed frame file in public/.

Source: DCI _postbuild_check.py:check_embed_locks, lock L2 (EMBED-L2). For each
(slug, url_path) of the site's slug->URL mapping, the frame is url_path with
'.html' replaced by the frame suffix ('-embed.html'), and it must be a file in
the public dir. The mapping is read from the site by a declared path: either a
JSON object file, or a .py file whose top-level assignment named by option
`mapping_name` is evaluated with ast.literal_eval (site code is never imported
or executed).
"""

import ast
import json

NAME = "embed_frame_files"
DESCRIPTION = ("Every calculator slug in the site's slug->URL mapping has an "
               "embed frame file (<page>-embed.html) in public/.")
REQUIRES = {
    "slug_to_url": "file holding the calculator slug -> '/page.html' mapping: a "
                   ".py file (top-level dict literal named by option "
                   "mapping_name) or a .json object",
}
OPTIONS = {
    "mapping_name": "CALCULATOR_SLUG_TO_URL",
    "frame_suffix": "-embed.html",
}


def _load_mapping(ctx):
    path = ctx.data["slug_to_url"]
    src = ctx.read_text(path)
    if str(path).endswith(".json"):
        mapping = json.loads(src)
    else:
        name = ctx.options["mapping_name"]
        mapping = None
        for node in ast.parse(src, filename=str(path)).body:
            if isinstance(node, ast.Assign):
                targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                targets = [node.target.id]
            else:
                continue
            if name in targets and node.value is not None:
                mapping = ast.literal_eval(node.value)  # last assignment wins
        if mapping is None:
            raise ValueError("no top-level literal assignment %r in %s"
                             % (name, ctx.rel(path)))
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError("slug->URL mapping is not a non-empty dict")
    return mapping


def check(ctx):
    suffix = ctx.options["frame_suffix"]
    findings = []
    for slug, url_path in sorted(_load_mapping(ctx).items()):
        url_path = str(url_path)
        if not url_path.endswith(".html"):
            findings.append(ctx.finding(
                "(site)", "%s: mapped URL does not end in .html, frame name "
                "cannot be derived" % slug, url_path))
            continue
        frame = url_path.lstrip("/")[:-len(".html")] + suffix
        if not (ctx.public_dir / frame).is_file():
            findings.append(ctx.finding(
                frame, "%s: no embed frame %s/%s" % (slug, ctx.public_dir.name, frame),
                "%s -> %s" % (slug, url_path)))
    return findings
