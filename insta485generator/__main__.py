"""Build static HTML site from directory of HTML templates and plain files."""

import pathlib
import json
import sys
import shutil
import click
import jinja2


@click.command()
@click.argument("input_dir", nargs=1, type=click.Path(exists=True))
@click.option("-o", "--output",
              type=click.Path(), default=None, help="Output directory.")
@click.option("-v", "--verbose", is_flag=True, help="Print more output.")
def main(input_dir, output, verbose):
    """Templated static website generator."""
    input_dir = pathlib.Path(input_dir)
    output_dir = pathlib.Path(output) if output else input_dir / 'html'

    # Check if output directory exists
    if output_dir.exists():
        click.echo("insta485generator error: Output directory " +
                   f"'{output_dir}' already exists.", err=True)
        sys.exit(1)
    else:
        output_dir.mkdir(parents=True, exist_ok=False)

    # Debug prints
    if verbose:
        print(f"DEBUG input_dir={input_dir}")
        print(f"DEBUG output_dir={output_dir}")

    # Read configuration file using context manager
    config_file = input_dir / 'config.json'
    if not config_file.exists():
        click.echo("insta485generator error: " +
                   f"'{config_file}' not found", err=True)
        sys.exit(1)

    try:
        with open(config_file, encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        click.echo(f"insta485generator error: '{config_file}'\n{e}", err=True)
        sys.exit(1)

    # Set up Jinja2 environment
    template_dir = input_dir / 'templates'
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
    )

    # Render templates and write output
    try:
        for item in config:
            template = template_env.get_template(item['template'])
            # in this case, item['template'] is 'index.html'
            rendered_content = template.render(item['context'])
            output_file = output_dir / item['url'].lstrip('/')
            # the lstrip() method returns a copy of the
            # string with leading characters removed
            output_file.parent.mkdir(parents=True, exist_ok=True)
            # the default output file is index.html
            output_file = output_file / 'index.html'
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with output_file.open('w') as f:
                f.write(rendered_content)
    except jinja2.TemplateNotFound as e:
        click.echo("insta485generator error: " +
                   f"'{e.filename}'\n{e.message}", err=True)
        sys.exit(1)

    # Copy static files
    def copy_static_files(static_dir, output_dir):
        if static_dir.exists():
            for item in static_dir.iterdir():
                dest = output_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy(item, dest)

    copy_static_files(input_dir / 'static', output_dir)


if __name__ == "__main__":
    main()
