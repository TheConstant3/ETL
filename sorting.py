import random


def quick_sort_columns(nums, fst, lst):
    if fst >= lst:
        return

    i, j = fst, lst
    pivot = nums[0][random.randint(fst, lst)]

    while i <= j:
        while nums[0][i] < pivot:
            i += 1
        while nums[0][j] > pivot:
            j -= 1
        if i <= j:
            for num in nums:
                num[i], num[j] = num[j], num[i]
            i, j = i + 1, j - 1
    quick_sort_columns(nums, fst, j)
    quick_sort_columns(nums, i, lst)


def quick_sort_rows(nums, fst, lst):
    if fst >= lst:
        return

    i, j = fst, lst
    pivot = nums[random.randint(fst, lst)][0]

    while i <= j:
        while nums[i][0] < pivot:
            i += 1
        while nums[j][0] > pivot:
            j -= 1
        if i <= j:
            for x in range(0, len(nums[0])):
                nums[i][x], nums[j][x] = nums[j][x], nums[i][x]
            i, j = i + 1, j - 1
    quick_sort_rows(nums, fst, j)
    quick_sort_rows(nums, i, lst)
