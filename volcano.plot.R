install.packages('manhattanly', dependencies = TRUE)
suppressMessages(library('manhattanly',quietly=TRUE,warn.conflicts = FALSE))

args = commandArgs(trailingOnly=TRUE)

input_split <- strsplit(args[1], "\\/")[[1]]
# Create environment variables

input_csv <- args[1]
current_hashed_folder <- getwd()

result <- read.csv(input_csv,check.names = F)
result <- result[!is.na(result$ttest_pval),]

colnames(result)[which(names(result) == "ttest_pval")] <- "P"
colnames(result)[which(names(result) == "Log2FoldChange")] <- "EFFECTSIZE"
if (args[2] == 'True'){
	volcano <- volcanoly(result, snp = "Metabolite", gene = "Formula",effect_size_line = c(-0.136, 0.136),genomewideline = -log10(0.05),xlab = 'log2FC',ylab='-log10(p)')
} else 
{ volcano <- volcanoly(result, snp = "Metabolite", gene = "Formula",genomewideline = -log10(0.05),xlab = 'log2FC',ylab='-log10(p)')

}


iframe_dir = paste(current_hashed_folder,'/iframe',sep="")
dir.create(iframe_dir)
volcano_dir = paste(current_hashed_folder,'/output/volcano/volcano.pdf',sep="")
pdf(pdf_name)

title = paste(file_name,'.volcano.html')
title = gsub(" ", "", title, fixed = TRUE)
title = gsub(".csv", "", title, fixed = TRUE)

dir_to_remove = gsub(".html", "", title, fixed = TRUE)
dir_to_remove = paste(dir_to_remove,'_files')
dir_to_remove = gsub(" ", "", dir_to_remove, fixed = TRUE)



htmlwidgets::saveWidget(volcano,file = title,selfcontained=FALSE)
#unlink(dir_to_remove, recursive=TRUE)

setwd('..')
setwd('..')

