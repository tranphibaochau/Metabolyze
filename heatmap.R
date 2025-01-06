library(pheatmap)
suppressMessages(library('pheatmap',quietly=TRUE,warn.conflicts = FALSE))
suppressMessages(library(dplyr,quietly=TRUE,warn.conflicts=FALSE))
current_hashed_folder <- getwd()

args = commandArgs(trailingOnly=TRUE)

# Generate Heatmap for each corrected comparison using different pvalue cutoffs
data_file_path <- args[1]
group_file_path <- args[2]
pvalue_cutoff <- as.numeric(args[3])
scale_type <- args[4]
cluster_rows <- as.logical(args[5])
cluster_cols <- as.logical(args[6])
show_rownames <- as.logical(args[7])
fontsize <- as.numeric(args[8])

cell_colors = colorRampPalette(c("#043177", "#244B88", "#FAFAFA",
                                 "#C62E2E", "#BF0F0F"))(50)
data <- read.csv(data_file_path, sep="\t", check.names = FALSE)
data$Metabolite <- make.unique(data$Metabolite) # make the names of metabolite unique, even if they have the same name
rownames(data) <- data$Metabolite

groups <- read.csv(group_file_path, sep="\t")
rownames(groups) <- groups$id

groups_assignment <- subset(groups, select = -c(File, id))
groups_assignment <- subset(groups_assignment, Group != "Blank")

unique_groups = as.list(unique(groups_assignment$Group))
unique_group_pairs <- combn(unique_groups,2,simplify = FALSE)


sampleTable <- groups[which(groups$Group != 'Blank'),]
subset_color <- sampleTable[!duplicated(sampleTable[c("Group","Color")]),]
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

for (group_pair in unique_group_pairs) {
  cur_groups <- subset(groups_assignment, (groups_assignment$Group == group_pair[1] | groups_assignment$Group == group_pair[2]))
  p_val_col = paste(group_pair[1],"_vs_",group_pair[2],"_ttest_pval",sep="")
  cur_data <- data[, colnames(data) %in% append(rownames(cur_groups),p_val_col) , drop = FALSE]
  cur_data <- cur_data[cur_data[[p_val_col]] < 0.05,]
  cur_data <- cur_data[, !colnames(cur_data) %in% p_val_col]
  cur_data <- na.omit(cur_data)
  cur_data$std <- apply( cur_data, 1, sd )
  cur_data <- cur_data[cur_data$std > 0,]
  cur_data <-subset(cur_data, select = -c(std))
  pdf_name = paste(current_hashed_folder,"/output/heatmap/",group_pair[1],"_vs_",group_pair[2],'.pdf',sep="")
  pdf(pdf_name)
  
  pheatmap(cur_data,fontsize = fontsize, show_rownames = show_rownames,
           scale = scale_type, cluster_rows = cluster_rows, annotation_colors = ann_color,
           cluster_cols = cluster_cols, annotation_col = col_anno, color =  cell_colors,
           fontsize_col = fontsize, fontsize_row = fontsize)
  
  
  garbage <- dev.off()
}

for (group_pair in unique_group_pairs) {
  cur_groups <- subset(groups_assignment, (groups_assignment$Group == group_pair[1] | groups_assignment$Group == group_pair[2]))
  p_val_col = paste(group_pair[1],"_vs_",group_pair[2],"_ttest_pval",sep="")
  cur_data <- data[, colnames(data) %in% append(rownames(cur_groups),p_val_col) , drop = FALSE]
  cur_data <- cur_data[cur_data[[p_val_col]] < 0.05,]
  cur_data <- cur_data[, !colnames(cur_data) %in% p_val_col]
  cur_data <- na.omit(cur_data)
  cur_data$std <- apply( cur_data, 1, sd )
  cur_data <- cur_data[cur_data$std > 0,]
  cur_data <-subset(cur_data, select = -c(std))
  pdf_name = paste(current_hashed_folder,"/output/iframe/",group_pair[1],"_vs_",group_pair[2],'.pdf',sep="")
  pdf(pdf_name)
  
  pheatmap(cur_data,fontsize = fontsize, show_rownames = show_rownames,
           scale = scale_type, cluster_rows = cluster_rows, annotation_colors = ann_color,
           cluster_cols = cluster_cols, annotation_col = col_anno, color =  cell_colors,
           fontsize_col = fontsize, fontsize_row = fontsize)
  
  
  garbage <- dev.off()
}

