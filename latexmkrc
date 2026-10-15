# Read automatically by latexmk (editors such as VS Code, TeXstudio, TeXShop,
# and a terminal run of latexmk). You do not need to edit it.
#
# When the PDF goes to an output folder such as build/, LaTeX writes one .aux
# file per \include'd chapter into a matching subfolder (build/chapters/).
# Those folders do not exist on the first compile, so the first run would
# stop with "I can't write on file chapters/....aux". This file creates the
# folders before each LaTeX run. It changes nothing else.
use File::Path qw(make_path);
use File::Glob qw(bsd_glob);

$pdflatex = 'internal rpi_mirror_dirs pdflatex %O %S';
$xelatex  = 'internal rpi_mirror_dirs xelatex %O %S';
$lualatex = 'internal rpi_mirror_dirs lualatex %O %S';

sub rpi_mirror_dirs {
    my $out = $aux_dir ne '' ? $aux_dir : $out_dir;
    if ($out ne '' && $out ne '.') {
        my $walk;
        $walk = sub {
            my ($dir, $depth) = @_;
            return if $depth > 3;
            opendir(my $handle, $dir) or return;
            my @names = grep { !/^\./ } readdir($handle);
            closedir($handle);
            for my $name (@names) {
                my $path = ($dir eq '.') ? $name : "$dir/$name";
                next unless -d $path && !-l $path;
                next if $name eq 'build' || $name eq 'dist' || $name eq '_local';
                make_path("$out/$path") if bsd_glob("$path/*.tex");
                $walk->($path, $depth + 1);
            }
        };
        $walk->('.', 1);
    }
    return system(@_);
}
