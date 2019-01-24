.ignoreList <- c("res.txt", "qrel.txt")

args <- commandArgs(TRUE)
if(length(args) != 1)
  stop("Usage: Rscript summary.R <directory>")

path <- args[1]

for(f in list.files(path, ".+\\.txt$")) {
  if(!f %in% .ignoreList) {
    cat(f, "\n")
    d <- read.table(file.path(path, f), header = FALSE)

    d <- d[-nrow(d), ncol(d)] # only last column, remove last row (mean over all queries)
    statistics <- c(mean = mean(d), `std.dev` = sd(d), `std.err.` = sd(d)/sqrt(length(d)), median = median(d))

    png(file.path(path, paste0(f, ".png")), 480, 320)
    par(mar = c(3,3,0,7), mgp = c(1.8,.5,0))
    hist(d, xlim = 0:1, main = "", xlab = tools::file_path_sans_ext(f))
    rug(statistics[1])

    legend("topright", inset = c(-.3,0), paste0(names(statistics), " = ", round(statistics, 3)), bty = "n", xpd = TRUE)
    dev.off()
  }
}
