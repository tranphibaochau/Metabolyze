#!/usr/bin/env Rscript
#sink("/dev/null")


#repos='http://cran.us.r-project.org'
#list.of.packages <- c("pheatmap", "string")
#new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
#if(length(new.packages)) install.packages(new.packages)


suppressMessages(library('pheatmap',quietly=TRUE,warn.conflicts = FALSE))
suppressMessages(library(dplyr,quietly=TRUE,warn.conflicts=FALSE))
args = commandArgs(trailingOnly=TRUE)

# Generate Heatmap for each corrected comparison using different pvalue cutoffs
comparison <- args[1]
group_ids <- args[2]
pvalue <- args[3]
scale <- args[4]
fontsize <- args[5]
width <- args[6]
height <- args[7]
current_hashed_folder <- getwd()

heatmap <- function(comparison, group_ids, pvalue){ # scale, fontsize, width, height
  directory <- strsplit(comparison, "\\\\")[[1]]
  comparison_name <- directory[-1]
  pvalue <- as.double(pvalue)
  fontsize <- as.numeric(fontsize)
  width <- as.numeric(width)
  height <- as.numeric(height)
  counts <-read.csv(comparison, sep="\t", check.names = F)
  #counts$ttest_pval <- as.numeric(levels(counts$ttest_pval))[counts$ttest_pval]
  counts <- counts[which(counts$ttest_pval < pvalue), ]
  colnames(counts)[which(names(counts) == "Metabolite")]  <- 'Delete'
  colnames(counts)[which(names(counts) == "RT.Start..min.")]  <- 'Delete'

  # remove std counts
  require(dplyr,quietly = TRUE)



  ## Heatmap Color Annotations
  sampleTable <- read.csv(group_ids, sep="\t")
  print(head(sampleTable))
  sampleTable <- sampleTable[which(sampleTable$Group != 'Blank'),]

  subset_color <- sampleTable[!duplicated(sampleTable[c("Group","Color")]),]

  sampleTable <- sampleTable %>% filter(Group != "Blank")
  columns.interest <- c('id','Group')
  sampleTable <- sampleTable[,columns.interest]
  sampleTable <- as.data.frame(sampleTable)
  sampleTable$id   <- sampleTable$id

  colnames(sampleTable)<- c('File','Condition')
  col_anno <- as.data.frame(sampleTable$Condition)
  names(col_anno) <- c('Condition')
  row.names(col_anno)<- sampleTable$File

  Color <- as.character(subset_color$Color)
  names(Color) <- as.character(subset_color$Group)
  ann_color <- list(Color)
  names(ann_color) <- 'Condition'


  columns.interest <- c('Metabolite',row.names(col_anno))
  counts <- counts[, which(names(counts) %in% columns.interest)]

  row.names(counts) <- counts$Metabolite
  counts$Metabolite <- NULL


  std =apply( counts, 1, sd )
  df =as.data.frame(std)
  df$gene = row.names(df)

  datasetnew <- df[df$std>0,]
  colnames(datasetnew) <- c('std','metabolite')

  counts$metabolite <- row.names(counts)
  merged <- merge(counts,datasetnew,on='metabolite')
  row.names(merged) <- merged$metabolite

  merged$metabolite <- NULL
  merged$std <- NULL

  title = paste(length(colnames(merged)), 'x' ,nrow(merged))
  title= gsub(" ", "", title, fixed = TRUE)


  # Set heatmap colors

  cell_colors = colorRampPalette(c("#043177", "#244B88", "#FAFAFA",
                                   "#C62E2E", "#BF0F0F"))(50)



  output_folder = paste(current_hashed_folder, '/heatmap', sep="")
  dir.create(output_folder)
  pdf_name = paste(current_hashed_folder,'/output/heatmap/heatmap.pdf',sep="")
  pdf(pdf_name)


  if (nrow(merged) > 200){row_name_toggle <- FALSE} else { row_name_toggle <- TRUE}
  pheatmap(as.matrix(merged), color = cell_colors,
           border_color = NA,show_rownames = row_name_toggle,fontsize = fontsize,
           scale = scale, cluster_rows = T, annotation_colors = ann_color,
           main = title,annotation_col = col_anno,
           cluster_cols = T,
           fontsize_col = 10, width = width, height = height)

  garbage <- dev.off()

  iframe_dir = paste(current_hashed_folder,'/iframe',sep="")
  dir.create(iframe_dir)
  pdf_name = paste(current_hashed_folder,'/output/iframe/heatmap.pdf',sep="")
  pdf(pdf_name)

  pheatmap(as.matrix(merged), color = cell_colors,
           border_color = NA,show_rownames = row_name_toggle,fontsize = fontsize,
           scale = scale, cluster_rows = T, annotation_colors = ann_color,
           main = title,annotation_col = col_anno,
           cluster_cols = T,
           fontsize_col = 10, width = width, height = height)

  garbage <- dev.off()
}

heatmap(comparison, group_ids, pvalue)
# heatmap(comparison, group_ids, pvalue, scale, fontsize, width, height)